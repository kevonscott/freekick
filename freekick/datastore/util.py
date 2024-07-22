from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from functools import cache, partial

import dask.dataframe as dd
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from sqlalchemy import select

from freekick import DATA_DIR, _logger

from .model import Game, Team
from .repository import AbstractRepository


class TeamNotFoundError(Exception):
    pass


class League(Enum):
    """Container for the supported leagues"""

    EPL = "epl"


@dataclass(frozen=True)
class TeamName:
    code: str
    name: str


class Backend(Enum):
    PANDAS = 1
    DASK = 2


class Season(Enum):
    """List of supported seasons."""

    S_2024_2025 = "S_2024_2025"
    S_2023_2024 = "S_2023_2024"
    S_2022_2023 = "S_2022_2023"
    S_2021_2022 = "S_2021_2022"
    S_2020_2021 = "S_2020_2021"
    S_2019_2020 = "S_2019_2020"
    S_2018_2019 = "S_2018_2019"
    S_2017_2018 = "S_2017_2018"
    S_2016_2017 = "S_2016_2017"
    S_2015_2016 = "S_2015_2016"
    S_2014_2015 = "S_2014_2015"
    S_2013_2014 = "S_2013_2014"
    S_2012_2013 = "S_2012_2013"
    S_2011_2012 = "S_2011_2012"
    S_2010_2011 = "S_2010_2011"
    S_2009_2010 = "S_2009_2010"
    S_2008_2009 = "S_2008_2009"
    S_2007_2008 = "S_2007_2008"
    S_2006_2007 = "S_2006_2007"
    S_2005_2006 = "S_2005_2006"
    S_2004_2005 = "S_2004_2005"
    S_2003_2004 = "S_2003_2004"
    S_2002_2003 = "S_2002_2003"
    S_2001_2002 = "S_2001_2002"
    S_2000_2001 = "S_2000_2001"
    S_1999_2000 = "S_1999_2000"
    S_1998_1999 = "S_1998_1999"
    S_1997_1998 = "S_1997_1998"
    S_1996_1997 = "S_1996_1997"
    S_1995_1996 = "S_1995_1996"
    S_1994_1995 = "S_1994_1995"
    S_1993_1994 = "S_1993_1994"
    CURRENT = S_2021_2022


def season_to_int(s: str | Season):
    if isinstance(s, Season):
        s = s.value
    return np.int64(s.removeprefix("S_").replace("_", ""))


def fix_team_name(name: str) -> str:

    match name:
        case "Tottenham":
            return "Tottenham Hotspur"
        case "Leeds":
            return "Leeds United"
        case "Brighton and Hove Albion":
            return "Brighton"
        case "Hull":
            return "Hull City"
        case "QPR":
            return "Queens Park Rangers"
        case "Man United" | "MUN":
            return "Manchester United"
        case "Nott'm Forest":
            return "Nottingham Forest"
        case "West Ham":
            return "West Ham United"
        case "Wolverhampton Wanderers" | "Wolverhampton":
            return "Wolves"
        case "West Bromwich Albion":
            return "West Brom"
        case "STO" | "Stoke":
            return "Stoke City"
        case " City":
            return "Norwich"
        case "Newcastle United":
            return "Newcastle"
        case "Leicester":
            return "Leicester City"
        case "Man City":
            return "Manchester City"
        case "Sheffield Weds":
            return "Sheffield Wednesday"
        case _:
            return name


class DataUtils(ABC):
    @abstractmethod
    def get_team_code(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_team_id(self, *args, **kwargs):
        pass

    @abstractmethod
    def add_teams(self, teams: list):
        pass

    @staticmethod
    def new_team_id(team_code: str):
        return abs(hash(team_code))


class DBUtils(DataUtils):
    @staticmethod
    def get_team_code(
        league: str,
        team_name: str,
        repository: AbstractRepository,
    ) -> str:
        """Looks up a team's code given its full name.

        Parameters
        ----------
        repository :
            Database abstraction interface to use for db interaction
        league :
            The teams 3 letter code
        team_name :
            Full name of the team
        Returns
        -------
        str
            Three letter code or integer representing the team. None if team
            cannot  be found.

        Raises
        ------
        TeamNotFoundError
            Value error if invalid team or not found.

        """
        statement = (
            select(Team)
            .where(Team.name == team_name)
            .where(Team.league == league)
        )
        entity = repository.session.scalars(statement).one_or_none()
        if not entity:
            raise TeamNotFoundError(f"Team code not found for '{team_name}'.")

        return entity.code

    @staticmethod
    def get_team_id(team_code: str, repository: AbstractRepository) -> int:
        """Looks up a team's ID given its team_code.

        :param team_code: A teams unique code
        :param repository: Database abstraction interface for db interaction
        :raises TeamNotFoundError: Raised when team is not found.
        :return: Three Integer representing the team.
        """
        statement = select(Team).where(Team.code == team_code)
        entity = repository.session.scalars(statement).one_or_none()
        if not entity:
            raise TeamNotFoundError(f"Team ID not found for '{team_code}'.")
        return entity.team_id

    @staticmethod
    def get_teams(
        repository: AbstractRepository,
        league: str,
        season: Season,
    ) -> tuple[str, list[TeamName]]:
        """Get list of teams for a specific season and league.

        :param repository: Repository to use for db operations
        :param league: League code
        :param season: Season to query for
        :raises ValueError: Raises when no teams are found.
        :return: Tuple of season name and list if TeamNames
        """
        statement = (
            select(Team)
            .join(Game, Game.home_team == Team.code)
            .where(Game.league == league)
            .where(Game.season == season.value)
        )
        entities = repository.session.scalars(statement).all()
        if not entities:
            raise ValueError(
                f"No teams found for the following league: {league}"
            )
        teams: set = set()
        for entity in entities:
            teams.add(TeamName(code=entity.code, name=entity.name))
        return season.value, list(teams)

    @staticmethod
    def create_team_model(df: pd.DataFrame) -> list[Team]:
        """Create db ORM Team models from dataframe.

        :param df: DataFrame with team data
        :return: List of DB ORM Team models
        """
        teams = []
        for _, series in df.iterrows():
            team = Team(
                code=series["code"],
                name=series["name"],
                league=series["league"],
                team_id=series["team_id"],
            )
            teams.append(team)
        return teams

    @staticmethod
    def create_game_model(df: pd.DataFrame, repository) -> list[Game]:
        """Create db ORM Game models from dataframe.

        :param df: DataFrame with game data
        :param repository: Repository to use for db operations
        :return: List of DB ORM Game models
        """
        team_code = partial(
            DBUtils.get_team_code, repository=repository, league="epl"
        )
        df = df.dropna(subset=["AwayTeam", "HomeTeam"])
        games = []
        df["Date"] = pd.to_datetime(df["Date"])
        df["FTHG"] = df["FTHG"].fillna(0).astype("int64")
        df["FTAG"] = df["FTAG"].fillna(0).astype("int64")
        df["Attendance"] = df["Attendance"].fillna(0).astype("int64")
        # Convert team names to team codes
        df["AwayTeam"] = df["AwayTeam"].apply(lambda x: team_code(team_name=x))
        df["HomeTeam"] = df["HomeTeam"].apply(lambda x: team_code(team_name=x))
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
                season=series["season"],
            )
            games.append(game)
        return games

    @abstractmethod
    def add_teams(self, teams: list):
        pass


class CSVUtils(DataUtils):
    @staticmethod
    def get_team_code(league: str, team_name: str, **kwargs) -> str:
        """Looks up a team's code name given its full name.

        :param league: League code
        :param team_name: Full name of the team
        :param team_code: _description_, defaults to None
        :return: Team Code
        """
        team_name = fix_team_name(name=team_name)
        teams_df = CSVUtils.load_teams_csv()
        code = teams_df[
            (teams_df["name"] == team_name) & (teams_df["league"] == league)
        ]["code"].iloc[0]
        return code

    @staticmethod
    def get_team_id(team_code: str) -> str:
        """Looks up a team's id given its code.

        :param team_code: I teams unique code
        :return: Team ID
        """
        teams_df = CSVUtils.load_teams_csv()
        team_id = teams_df[(teams_df["code"] == team_code)]["team_id"].iloc[0]
        return team_id

    @abstractmethod
    def add_teams(self, teams: list):
        pass

    @staticmethod
    @cache
    def load_teams_csv():
        file_path = str(DATA_DIR / "processed" / "team.csv")
        return pd.read_csv(file_path)


class DataStore(Enum):
    CSV = CSVUtils
    DATABASE = DBUtils
    DEFAULT = CSV


DATA_UTIL = DataStore.DEFAULT.value

COLUMNS = {
    "Date": "date",
    "Time": "time",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHG": "home_goal",
    "FTAG": "away_goal",
    "FTR": "result",
    "season": "season",
    "Attendance": "attendance",
}

LEAGUE_URI_LOOKUP = {
    League.EPL: "premier-league",
    # League.BUNDESLIGA: "bundesliga"
}


class DataScraper:
    """Data class used to fetch various soccer data from open source."""

    def __init__(self, league: League) -> None:
        self.urls = {
            "team_rating": "https://projects.fivethirtyeight.com/soccer-predictions",
            "player_rating": "https://www.whoscored.com/Statistics",
        }  # Dict of data type to scraping url
        self.league: League = league

    def _parse_team_rating_request(self, soup: BeautifulSoup, type: str):
        """Parse a BS4 object for team or player rating data.

        Parameters
        ----------
        soup :
            BeautifulSoup query object.
        type : str
            _description_

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        ValueError
            _description_
        """
        # eg 'Updated Feb. 5, 2022, at 8:03 PM'
        last_updated_tag = soup.find("p", {"class": "timestamp"})
        if not last_updated_tag:
            raise NameError("Tag 'timestamp' no found on page content.")
        last_updated = last_updated_tag.get_text()
        last_updated_split = last_updated.split(" ")[1:4]
        d_m_y = (
            last_updated_split[1].strip(",")
            + "/"
            + last_updated_split[0].strip(".").capitalize()
            + "/"
            + last_updated_split[2].strip(",")
        )
        try:  # First try full month name
            last_updated_datetime = datetime.strptime(d_m_y, "%j/%B/%Y")
        except ValueError:  # The try 3 letter month name
            try:
                last_updated_datetime = datetime.strptime(d_m_y, "%j/%b/%Y")
            except ValueError:
                day, month, year = d_m_y.split("/")
                if month == "Sept":
                    last_updated_datetime = datetime(int(year), 9, int(day))
                else:
                    raise
        if type == "team_rating":
            team_ranking = (
                {}
            )  # { teams: {team_name: {overall: <rank>, offense: <rank>, defense: <rank>}, last_updated: 'string' }
            team_ranking["last_updated"] = last_updated_datetime
            team_rows = soup.find_all("tr", {"class": "team-row"})
            for team in team_rows:
                team_name = team.get("data-str")
                all_ratings = team.find_all("td", {"class": ["rating"]})
                team_overall_rating = None
                team_defensive_rating = None
                team_offensive_rating = None
                for rating in all_ratings:
                    classes = rating.get("class")
                    team_overall_rating = (
                        float(rating.get_text())
                        if "overall" in classes
                        else team_overall_rating
                    )
                    team_defensive_rating = (
                        float(rating.get_text())
                        if "defense" in classes
                        else team_defensive_rating
                    )
                    team_offensive_rating = (
                        float(rating.get_text())
                        if "offense" in classes
                        else team_offensive_rating
                    )
                team_ranking[team_name] = {
                    "overall": team_overall_rating,
                    "offense": team_defensive_rating,
                    "defense": team_offensive_rating,
                }
            ranking_df = pd.DataFrame(team_ranking)
            ranking_df = ranking_df.reset_index().set_index(
                ["last_updated", "index"]
            )  # multi index df
            ranking_df.index.set_names(["date", "ranking"], inplace=True)
            ranking_df = ranking_df.unstack()  # type: ignore[assignment]

        elif type == "player_rating":
            player_ranking = {}
            player_ranking["last_updated"] = last_updated_datetime
            raise NotImplementedError
        else:
            raise ValueError(
                f"Invalid scraper type {type}. Valid choices {self.urls.keys()}"
            )
        return ranking_df

    def scrape_team_rating(self, persists: bool = False, use_db: bool = False):
        data_type = "team_rating"
        league_end_point = LEAGUE_URI_LOOKUP[self.league]
        team_rating_uri = f"{self.urls[data_type]}/{league_end_point}/"
        team_ranking_csv = str(
            DATA_DIR / "processed" / f"{self.league.value}_team_ranking.csv"
        )

        _logger.info(
            f"Scraping {self.league} '{data_type}' data from {team_rating_uri}"
        )
        with requests.Session() as session:
            page = session.get(url=team_rating_uri)
        page.raise_for_status()
        _logger.info(f"Request status code: {page.status_code}")

        soup = BeautifulSoup(page.content, "html.parser")
        df = self._parse_team_rating_request(soup=soup, type=data_type)
        if persists:
            if use_db:
                raise NotImplementedError
            else:
                _logger.info("Updating csv....")
                exist_df = pd.read_csv(
                    team_ranking_csv,
                    index_col=["date", "ranking"],
                    parse_dates=True,
                )
                df = df.stack()
                new_df = pd.concat([exist_df, df], axis=0)
                new_df.to_csv(team_ranking_csv, index=False)
        else:
            _logger.info("Unstacking dataframe for better visibility...")
            _logger.info(df)


class BaseData(ABC):
    _processed_data_path = DATA_DIR / "processed"
    _raw_data_path = DATA_DIR / "raw"
    repository: AbstractRepository | None = None

    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def update_current_season(self):
        pass

    @abstractmethod
    def clean_format_data(self, data: pd.DataFrame):
        pass

    @classmethod
    def _clean_format_data(cls, X: pd.DataFrame, league: League):
        """Cleans and formats DataFrame.

        Parameters
        ----------
        X:
            Pandas dataframe with soccer statistics
        league:
            Code name of the league
        """
        # A/-1: Away Team Win
        # D/0: Draw
        # H/1: Home Team Win
        X = X[COLUMNS.keys()]
        X = X.rename(columns=COLUMNS)
        X["result"] = np.where(
            X["result"] == "A", -1, np.where(X["result"] == "H", 1, 0)
        )
        X["date"] = pd.to_datetime(X["date"])
        X = X.dropna(
            subset=[
                "home_team",
                "away_team",
                "home_goal",
                "away_goal",
                "date",
            ],
            how="all",
        )
        X["time"] = pd.to_datetime(X["time"].bfill().ffill())
        X["attendance"] = X["attendance"].fillna(0)

        team_code = partial(
            DATA_UTIL.get_team_code, league.value, repository=cls.repository
        )
        X["home_team"] = X["home_team"].apply(team_code)
        X["away_team"] = X["away_team"].apply(team_code)
        X["home_team"] = X["home_team"].apply(DATA_UTIL.get_team_id)
        X["away_team"] = X["away_team"].apply(DATA_UTIL.get_team_id)
        X["season"] = X["season"].apply(
            lambda x: np.int64(x.removeprefix("S_").replace("_", ""))
        )
        X = X.reset_index(drop=True)
        return X

    def read_stitch_raw_data(
        self, league: League, persist: bool = False
    ) -> None:
        """Read multiple csv and stitch them together.

        Parameters
        ----------
        league :
            League Type.
        persist :
            If specified, new data file will be saved, by default False
        """

        dir_path = DATA_DIR / "raw" / league.value

        _logger.info(str(dir_path) + "/season*.csv")
        # Read all csv files in parallel
        df = dd.read_csv(
            str(dir_path) + "/season*.csv",
            dtype={"FTAG": "float64", "FTHG": "float64", "Time": "object"},
            usecols=COLUMNS.keys(),
            skip_blank_lines=True,
        ).compute()
        df["Date"] = pd.to_datetime(df["Date"], format="mixed")
        df["HomeTeam"] = df["HomeTeam"].apply(fix_team_name)
        df["AwayTeam"] = df["AwayTeam"].apply(fix_team_name)
        df = df.reset_index(drop=True)
        if persist:
            file_path = DATA_DIR / "processed" / f"{league.value}.csv"
            _logger.info(f"Persisting data: {file_path}")
            df.to_csv(file_path, index=False)
        _logger.info(f"df.shape:\n{df.shape}")


class EPLData(BaseData):

    def __init__(
        self,
        datastore: DataStore,
        repository: (
            AbstractRepository | None
        ) = None,  # required if Datastore.DB
        env: str = "development",
    ) -> None:
        super().__init__()
        self.env = env
        self.league = League.EPL
        self.repository = repository
        self.datastore = datastore
        if self.datastore == DataStore.DATABASE and not self.repository:
            raise ValueError(
                "Repository is required when using DataStore.DATABASE"
            )

    @cache
    def load(self) -> pd.DataFrame:
        """Load EPL data from DataStore."""

        def clean_date(d):
            """varying date formats so parse date in consistent format"""
            return parse(d) if isinstance(d, str) else np.nan

        match self.datastore:
            case DataStore.CSV:
                file_location = (
                    self._processed_data_path / f"{self.league.value}.csv"
                )
                data = pd.read_csv(
                    str(file_location),
                    parse_dates=["Time"],
                    date_format="mixed",
                )
            case DataStore.DATABASE:
                statement = select(Game).where(
                    Game.league == self.league.value
                )
                data = pd.read_sql_query(statement, con=self.repository.session.get_bind())  # type: ignore[union-attr]
            case _:
                raise NotImplementedError(
                    "Cannot extract data from {datastore} yet..."
                )
        data["Date"] = data["Date"].apply(clean_date)
        return self.clean_format_data(data=data)

    def update_current_season(self, persist: bool = False) -> None:
        """Get the latest data for the season.

        Parameters
        ----------
        persist : bool, optional
            If True. persists updated data to d_location, by default False
        """
        file_name = f"season_{Season.CURRENT.value.removeprefix('S_').replace('_', '-')}.csv"
        p = str(self._raw_data_path / self.league.value / file_name)

        division = "E0"
        season_format = "".join(
            [y[-2:] for y in Season.CURRENT.value.split("_")[-2:]]
        )  # e.g 9394, 2122..
        # example: "https://www.football-data.co.uk/mmz4281/2122/E0.csv"
        data_url = f"https://www.football-data.co.uk/mmz4281/{season_format}/{division}.csv"

        season_data = pd.read_csv(data_url)
        season_data["season"] = Season.CURRENT.value
        if persist:
            match self.datastore:
                case DataStore.CSV:
                    # Overwrite the file
                    # For csv, we dump the entire dataset
                    _logger.info("Saving/Updating file: ", p)
                    season_data.to_csv(p, index=False)
                case DataStore.DATABASE:
                    _logger.info("Updating Database...")
                    # Create game models
                    models_to_add = set()
                    game_models = DBUtils.create_game_model(
                        df=season_data, repository=self.repository
                    )
                    for model in game_models:
                        stmt = select(Game).where(
                            Game.season == model.season,
                            Game.league == model.league,
                            Game.home_team == model.home_team,
                            Game.away_team == model.away_team,
                            Game.date == model.date,
                        )
                        scalar = self.repository.session.scalars(stmt).one_or_none()  # type: ignore[union-attr]
                        # does not exists in db so add
                        if not scalar:
                            models_to_add.add(model)
                    if models_to_add:
                        self.repository.session.add_all(list(models_to_add))  # type: ignore[union-attr]
                        self.repository.session.commit()  # type: ignore[union-attr]
                case _:
                    raise NotImplementedError
        else:
            _logger.info(season_data)

    def clean_format_data(self, data: pd.DataFrame):
        return self._clean_format_data(X=data, league=self.league)


class BundesligaData(BaseData):
    pass
    # raise NotImplementedError


def get_league_data_container(league: str | League):
    if isinstance(league, str):
        league = League[league.upper()]
    match league:
        case League.EPL:
            return EPLData
        case _:
            raise NotImplementedError
