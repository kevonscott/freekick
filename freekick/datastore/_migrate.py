import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from freekick import DATA_DIR
from freekick.datastore.repository import SQLAlchemyRepository
from freekick.datastore.util import DBUtils

from .model import Base

DB_PATH = DATA_DIR / "freekick.db"
ENGINE = create_engine(f"sqlite:///{str(DB_PATH)}")
REPOSITORY = SQLAlchemyRepository(Session(ENGINE))


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

    def load_teams_from_csv():
        team_csv = DATA_DIR / "processed" / "team.csv"
        return pd.read_csv(team_csv)

    def load_games_from_csv():
        game_csv = DATA_DIR / "processed" / "epl.csv"
        return pd.read_csv(game_csv).dropna(how="all")

    with Session(engine) as session:
        # Populate teams
        teams_df = load_teams_from_csv()
        teams_models = DBUtils.create_team_model(df=teams_df)
        session.add_all(teams_models)
        # Initial commit needed here so DBUtils.create_game_model can query
        # team codes
        session.commit()

        # Populate games
        games_df = load_games_from_csv()
        games_models = DBUtils.create_game_model(
            df=games_df, repository=REPOSITORY
        )
        session.add_all(games_models)
        session.commit()
