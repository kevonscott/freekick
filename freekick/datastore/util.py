from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import cache, partial
from typing import Iterable, Optional, Any
from pathlib import Path

import dask.dataframe as dd
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from sqlalchemy import select

from freekick import DATA_DIR
from freekick.utils import _logger

from .model import Game, PythWpc, Team
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
    CURRENT = S_2023_2024


def season_to_int(s: str | Season) -> int:
    if isinstance(s, Season):
        s = s.value
    return int(s.removeprefix("S_").replace("_", ""))


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
    def get_team_code(self, *args: Any, **kwargs: Any) -> str:
        pass

    @abstractmethod
    def get_team_id(self, *args: Any, **kwargs: Any) -> int:
        pass

    @abstractmethod
    def add_teams(self, teams: list[Team], *args: Any, **kwargs: Any) -> None:
        pass

    def add_or_update_wpc_pyth(
        self,
        data: pd.DataFrame,
        league: League,
        repository: Optional[AbstractRepository] = None,
        **kwargs: Any,
    ) -> None:
        expected_columns = {
            "team",
            "season",
            "league",
            "win_percentage",
            "pythagorean_expectation",
            "last_update",
            "pyth_wpc_id",
        }
        _validate_cols(columns=data.columns, expected_columns=expected_columns)
        data = data[
            list(expected_columns)
        ].drop_duplicates()  # Drop any unnecessary columns
        # data["pyth_wpc_id"] = (
        #     data["team"].astype(str) + "_" + data["season"].astype(str)
        # )
        self.update_wpc_pyth(data=data, league=league, repository=repository)

    @abstractmethod
    def update_wpc_pyth(
        self, data: pd.DataFrame, league: League, *arg: Any, **kwargs: Any
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def load_wpc_pyth(self, league: League, season: Season) -> pd.DataFrame:
        raise NotImplementedError()

    @staticmethod
    def new_team_id(team_code: str) -> int:
        return abs(hash(team_code))

    @staticmethod
    def new_team(team_code: str, team_name: str, league: League) -> Team:
        team_id: int = DataUtils.new_team_id(team_code=team_code)
        return Team(
            code=team_code,
            name=team_name,
            league=league.value,
            team_id=team_id,
        )


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
        team_name = fix_team_name(team_name)
        statement = (
            select(Team)
            .where(Team.name == team_name)
            .where(Team.league == league)
        )
        entity = repository.session.scalars(statement).one_or_none()
        if not entity:
            raise TeamNotFoundError(f"Team code not found for '{team_name}'.")

        return str(entity.code)

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
        return int(entity.team_id)

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
        teams: set[TeamName] = set()
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
    def create_game_model(
        df: pd.DataFrame, repository: AbstractRepository
    ) -> list[Game]:
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
        df["Date"] = pd.to_datetime(df["Date"], format="mixed")
        df["FTHG"] = df["FTHG"].fillna(0).astype("int64")
        df["FTAG"] = df["FTAG"].fillna(0).astype("int64")
        if "Attendance" in df.columns:
            df["Attendance"] = df["Attendance"].fillna(0).astype("int64")
        else:
            df["Attendance"] = 0
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
                result=series["FTR"],
            )
            games.append(game)
        return games

    def add_teams(
        self, teams: list[Team], repository: AbstractRepository, **kwargs: Any
    ) -> None:
        for instance in teams:
            repository.add(instance)
        repository.commit()

    def _create_pyth_wpc_model(self, df: pd.DataFrame) -> list[PythWpc]:
        """Create PythWpc models from a DataFrame object.

        :param df: Data to parse.
        :return: List of PythWpc objects
        """
        if df.empty:
            return []

        pyth_wpc_list = []
        for _, row in df.iterrows():
            model = PythWpc(
                pyth_wpc_id=row["pyth_wpc_id"],
                team_code=row["team"],
                season=row["season"],
                league=row["league"],
                win_percentage=row["win_percentage"],
                pythagorean_expectation=row["pythagorean_expectation"],
                last_update=row["last_update"],
            )
            pyth_wpc_list.append(model)
        return pyth_wpc_list

    def update_wpc_pyth(
        self,
        data: pd.DataFrame,
        league: League,
        repository: AbstractRepository,
    ) -> None:
        _logger.info("Updating WPC and PYTH for %s", self.__class__.__name__)
        _logger.info("Persisting wpc_pyth for league: %s", league)
        models: list[PythWpc] = self._create_pyth_wpc_model(data)
        for model in models:
            db_model = repository.get(PythWpc, model.pyth_wpc_id)
            if db_model:
                # update instead. We only want to update some attrs
                for attr in {
                    "win_percentage",
                    "pythagorean_expectation",
                    "last_update",
                }:
                    setattr(db_model, attr, getattr(model, attr))
            else:
                # add new
                repository.add(model)
        repository.commit()
        _logger.info("WPC/PYTH update completed successfully!")

    def load_wpc_pyth(self, league: League, season: Season) -> pd.DataFrame:
        raise NotImplementedError


class CSVUtils(DataUtils):
    wpc_pyth_base_path = DATA_DIR / "processed"

    @staticmethod
    def get_team_code(league: str, team_name: str, **kwargs: Any) -> str:
        """Looks up a team's code name given its full name.

        :param league: League code
        :param team_name: Full name of the team
        :param team_code: _description_, defaults to None
        :return: Team Code
        """
        team_name = fix_team_name(name=team_name)
        teams_df = CSVUtils.load_teams_csv()
        code: str = teams_df[
            (teams_df["name"] == team_name) & (teams_df["league"] == league)
        ]["code"].iloc[0]
        return code

    @staticmethod
    def get_team_id(team_code: str, *arg: Any, **kwarg: Any) -> int:
        """Looks up a team's id given its code.

        :param team_code: I teams unique code
        :return: Team ID
        """
        teams_df = CSVUtils.load_teams_csv()
        team_id = teams_df[(teams_df["code"] == team_code)]["team_id"].iloc[0]
        return int(team_id)

    @staticmethod
    def add_teams(teams: list[Team], *args: Any, **kwargs: Any) -> None:
        team_df = pd.concat(
            [
                pd.DataFrame(
                    {
                        "code": [instance.code],
                        "name": [instance.name],
                        "league": [instance.league],
                        "team_id": [instance.team_id],
                    }
                )
                for instance in teams
            ]
        )
        teams_df = CSVUtils.load_teams_csv()
        teams_df = pd.concat([teams_df, team_df])

        file_path = str(DATA_DIR / "processed" / "team.csv")
        teams_df.to_csv(file_path, index=False)

    @staticmethod
    @cache
    def load_teams_csv() -> pd.DataFrame:
        file_path = str(DATA_DIR / "processed" / "team.csv")
        return pd.read_csv(file_path)

    def update_wpc_pyth(
        self, data: pd.DataFrame, league: League, *args: Any, **kwargs: Any
    ) -> None:
        _logger.info("Updating WPC and PYTH for %s", self.__class__.__name__)
        _logger.info("Updating CSV, overwrite existing one.")
        file_path = self.wpc_pyth_base_path / f"{league.value}_wpc_pyth.csv"
        data.to_csv(file_path, index=False)
        _logger.info("WPC/PYTH update complete!")

    def load_wpc_pyth(self, league: League, season: Season) -> pd.DataFrame:
        file_path = self.wpc_pyth_base_path / f"{league.value}_wpc_pyth.csv"
        data = pd.read_csv(file_path)
        season_int = season_to_int(season.value)
        data = data[data["season"] == season_int]
        if data.empty:
            raise ValueError(
                f"WPC-PYTH entry not found for league {league} and season "
                f"{season}. Was wpc_pyth previously computed?"
            )
        return data


class DataStore(Enum):
    CSV = CSVUtils
    DATABASE = DBUtils
    DEFAULT = DATABASE


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


@cache
def load_csv(*args: Any, **kwargs: Any) -> pd.DataFrame:
    return pd.read_csv(*args, **kwargs)  # type: ignore [no-any-return]


class DataScraper:
    """Data class used to fetch various soccer data from open source."""

    def __init__(self, league: League) -> None:
        self.urls = {
            "team_rating": "https://projects.fivethirtyeight.com/soccer-predictions",
            "player_rating": "https://www.whoscored.com/Statistics",
        }  # Dict of data type to scraping url
        self.league: League = league

    def _parse_team_rating_request(
        self, soup: BeautifulSoup, type: str
    ) -> pd.DataFrame:
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
            # {team_name: {overall: <rank>, offense: <rank>, defense: <rank>}, last_updated: 'string' }
            team_ranking = {}
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
                }  # type: ignore [assignment]
            ranking_df = pd.DataFrame(team_ranking)
            ranking_df = ranking_df.reset_index().set_index(
                ["last_updated", "index"]
            )  # multi index df
            ranking_df.index.set_names(["date", "ranking"], inplace=True)
            ranking_df = ranking_df.unstack()  # type: ignore [assignment]

        elif type == "player_rating":
            player_ranking = {}
            player_ranking["last_updated"] = last_updated_datetime
            raise NotImplementedError
        else:
            raise ValueError(
                f"Invalid scraper type {type}. Valid choices {self.urls.keys()}"
            )
        return ranking_df

    def scrape_team_rating(
        self, persists: bool = False, use_db: bool = False
    ) -> None:
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
                df = df.stack()  # type: ignore [assignment]
                new_df = pd.concat([exist_df, df], axis=0)
                new_df.to_csv(team_ranking_csv, index=False)
        else:
            _logger.info("Unstacking dataframe for better visibility...")
            _logger.info(df)


class BaseData(ABC):
    _processed_data_path = DATA_DIR / "processed"
    _raw_data_path = DATA_DIR / "raw"
    repository: Optional[AbstractRepository] = None
    datastore: Optional[DataStore] = None

    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def update_current_season(self) -> None:
        pass

    @abstractmethod
    def clean_format_data(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def _clean_format_data(
        self, X: pd.DataFrame, league: League
    ) -> pd.DataFrame:
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
        if not self.datastore:
            raise ValueError(f"{self.__class__.__name__}: DataStore required")
        should_convert_team_name_to_code = False
        if {"HomeTeam", "AwayTeam"}.issubset(X.columns):
            # We have the team names ("HomeTeam") and not team code "home_team"
            should_convert_team_name_to_code = True
        X = X.rename(columns=COLUMNS)
        X = X[COLUMNS.values()]
        X["result"] = np.where(
            X["result"] == "A", -1, np.where(X["result"] == "H", 1, 0)
        )
        X["date"] = pd.to_datetime(X["date"])
        X["day_of_week"] = X["date"].dt.day_of_week
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
        X["time"] = pd.to_datetime(X["time"].fillna("13:30"), format="mixed")
        X["attendance"] = X["attendance"].fillna(0)

        team_code = partial(
            self.datastore.value.get_team_code,
            league.value,
            repository=self.repository,
        )
        if should_convert_team_name_to_code:
            X["home_team"] = X["home_team"].apply(team_code)
            X["away_team"] = X["away_team"].apply(team_code)
        X["home_team"] = X["home_team"].apply(
            self.datastore.value.get_team_id, repository=self.repository
        )
        X["away_team"] = X["away_team"].apply(
            self.datastore.value.get_team_id, repository=self.repository
        )
        X["season"] = X["season"].apply(
            lambda x: int(x.removeprefix("S_").replace("_", ""))
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
        df = dd.read_csv(  # type: ignore [attr-defined]
            str(dir_path) + "/season*.csv",
            dtype={"FTAG": "float64", "FTHG": "float64", "Time": "object"},
            usecols=list(COLUMNS.keys()),
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
        _logger.info(f"df.shape: {df.shape}")

    def load_wpc_pyth(self, league: League, season: Season) -> pd.DataFrame:
        raise NotImplementedError()


def _validate_repository_for_db(repository: AbstractRepository | None) -> None:
    if not repository or not repository.session:
        raise ValueError(
            "Repository (with a session) is required when using "
            f"{DataStore.DATABASE.name}!"
        )

@cache
def _do_load_data(league: League, datastore: DataStore, repository: AbstractRepository, path: Path) -> pd.DataFrame:
    """Load data from DataStore."""

    def clean_date(d: Any) -> datetime | float:
        """varying date formats so parse date in consistent format"""
        return parse(d) if isinstance(d, str) else np.nan

    match datastore:
        case DataStore.CSV:
            file_location = path / f"{league.value}.csv"
            data = pd.read_csv(
                str(file_location),
                parse_dates=["Time"],
                date_format="mixed",
            )
            data["Date"] = data["Date"].apply(clean_date)
        case DataStore.DATABASE:
            _validate_repository_for_db(repository)
            statement = select(Game).where(
                Game.league == league.value
            )
            data = pd.read_sql_query(
                statement,
                con=repository.session.get_bind(),  # type: ignore [union-attr]
            )
        case _:
            raise NotImplementedError(
                f"Cannot extract data from datastore '{datastore}' yet..."
            )

    return data

class EPLData(BaseData):
    def __init__(
        self,
        datastore: DataStore,
        repository: Optional[
            AbstractRepository
        ] = None,  # required if Datastore.DB
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

    def load(self) -> pd.DataFrame:
        """Load EPL data from DataStore."""
        data = _do_load_data(
            league=self.league,
            datastore=self.datastore,
            repository=self.repository,
            path=self._processed_data_path
        )

        return self.clean_format_data(data=data)

    def update_current_season(self, persist: bool = False) -> None:
        """Get the latest data for the season.

        Parameters
        ----------
        persist : bool, optional
            If True. persists updated data to d_location, by default False
        """
        season = Season.CURRENT.value
        _logger.info(
            f"Updating data for season '{season}' and datastore '{self.datastore}'"
        )
        file_name = f"season_{season.removeprefix('S_').replace('_', '-')}.csv"
        p = str(self._raw_data_path / self.league.value / file_name)

        division = "E0"
        season_format = "".join(
            [y[-2:] for y in season.split("_")[-2:]]
        )  # e.g 9394, 2122,...
        # example: "https://www.football-data.co.uk/mmz4281/2122/E0.csv"
        data_url = f"https://www.football-data.co.uk/mmz4281/{season_format}/{division}.csv"

        _logger.info(f"Fetching {season} data from {data_url}...")
        season_data = self._read_csv(data_url)
        _logger.info("Loaded data successfully.")
        season_data["season"] = season
        if "Attendance" not in season_data.columns:
            season_data["Attendance"] = 0
        if persist:
            match self.datastore:
                case DataStore.CSV:
                    # Overwrite the file
                    # For csv, we dump the entire dataset
                    _logger.info(f"Saving/Updating raw season file: {p}")
                    season_data.to_csv(p, index=False)
                    _logger.info("Regenerating league data...")
                    self.read_stitch_raw_data(
                        league=self.league, persist=persist
                    )
                case DataStore.DATABASE:
                    _validate_repository_for_db(self.repository)
                    _logger.info("Updating Database...")
                    # Create game models
                    models_to_add = set()
                    game_models = DBUtils.create_game_model(
                        df=season_data,
                        repository=self.repository,  # type: ignore [arg-type]
                    )
                    for model in game_models:
                        stmt = select(Game).where(
                            Game.season == model.season,
                            Game.league == model.league,
                            Game.home_team == model.home_team,
                            Game.away_team == model.away_team,
                            Game.date == model.date,
                        )
                        scalar = self.repository.session.scalars(  # type: ignore [union-attr]
                            stmt
                        ).one_or_none()
                        # does not exists in db so add
                        if not scalar:
                            models_to_add.add(model)
                    if models_to_add:
                        self.repository.session.add_all(list(models_to_add))  # type: ignore[union-attr]
                        self.repository.session.commit()  # type: ignore[union-attr]
                case _:
                    raise NotImplementedError
        else:
            _logger.info(
                f"persist={persist}, not persisting changes in {self.datastore}!"
            )

    def clean_format_data(self, data: pd.DataFrame) -> pd.DataFrame:
        return self._clean_format_data(X=data, league=self.league)

    def _read_csv(self, uri: str) -> pd.DataFrame:
        return load_csv(uri)  # make a cached call.


class BundesligaData(BaseData):
    pass
    # raise NotImplementedError


@cache
def get_league_data_container(league: str | League) -> type[BaseData]:
    if isinstance(league, str):
        league = League[league.upper()]
    match league:
        case League.EPL:
            return EPLData
        case _:
            raise NotImplementedError


def _validate_cols(
    columns: Iterable[str], expected_columns: Iterable[str]
) -> None:
    """Validate columns we expect exists.

    :param columns: Iterable of columns to check
    :param expected_columns: Columns we expect to exists in columns.
    :raises ValueError: Raised when elements from expected_columns are missing.
    """
    column_diff = set(expected_columns) - set(columns)
    if column_diff:
        raise ValueError(f"Expected column(s) {column_diff} are missing.")
