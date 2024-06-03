from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .model import Base, Game, Team
from freekick import DATA_DIR

# TODO: Season in not included in this migration since I am carrying over the
# processed file form model/ai/data/processed/epl. We should read the raw data
# and regenerate db!!!

DB_PATH = DATA_DIR / "freekick.db"
ENGINE = create_engine(f"sqlite:///{str(DB_PATH)}")


def create_db(exists_ok: bool = True) -> None:
    """if exists_ok is false, drop all table and re-create"""

    if DB_PATH.exists() and not exists_ok:
        print("Recreating Database")
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=ENGINE)
        print("Creating Database....")
        Base.metadata.create_all(bind=ENGINE)
        print(f"Created DB: {DB_PATH}")
    elif DB_PATH.exists() and exists_ok:
        print(f"DB already exists, skipping: {DB_PATH}")
    else:
        Base.metadata.create_all(bind=ENGINE)
        print(f"Created DB: {DB_PATH}")


def _csv_to_sqlite_migration(engine=ENGINE):
    """Copy over data from csv, read csv and create models"""

    # Lock csv first?
    # create DB
    def load_teams_from_csv():
        team_csv = (
            Path(__file__).parent.parent
            / "model"
            / "ai"
            / "data"
            / "processed"
            / "team.csv"
        )
        return pd.read_csv(team_csv)

    def load_games_from_csv():
        game_csv = (
            Path(__file__).parent.parent
            / "model"
            / "ai"
            / "data"
            / "processed"
            / "epl.csv"
        )
        return pd.read_csv(game_csv).dropna(how="all")

    def create_team_models(df: pd.DataFrame) -> list[Team]:
        teams = []
        for _, series in df.iterrows():
            team = Team(
                code=series["code"],
                name=series["name"],
                league=series["league"],
            )
            teams.append(team)
        return teams

    def create_game_models(df: pd.DataFrame) -> list[Game]:
        df = df.dropna(subset=["AwayTeam", "HomeTeam"])
        games = []
        df["Date"] = pd.to_datetime(df["Date"])
        df["FTHG"] = df["FTHG"].fillna(0).astype("int64")
        df["FTAG"] = df["FTAG"].fillna(0).astype("int64")
        df["Attendance"] = df["Attendance"].fillna(0).astype("int64")
        for _, series in df.iterrows():
            game = Game(
                home_team=series["AwayTeam"],
                away_team=series["HomeTeam"],
                home_goal=series["FTHG"],
                away_goal=series["FTAG"],
                league="epl",
                date=series["Date"],
                time=series["Time"],
                attendance=series["Attendance"],
                # season=""  # TODO Backfill season later
            )
            games.append(game)
        return games

    with Session(engine) as session:
        # Populate teams
        teams_df = load_teams_from_csv()
        teams_models = create_team_models(teams_df)
        session.add_all(teams_models)

        # Populate games
        games_df = load_games_from_csv()
        games_models = create_game_models(games_df)
        session.add_all(games_models)

        session.commit()
