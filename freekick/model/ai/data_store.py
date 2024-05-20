from datetime import datetime
from functools import partial
from pathlib import Path
from pprint import pprint

import dask.dataframe as dd
import numpy as np
import pandas as pd
import pkg_resources
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse

from ...utils.freekick_config import load_config
from ..ai import SEASON, League, get_team_code

D_LOCATIONS = ["CSV", "DATABASE"]  # TODO: Use Enum instead


def load_data(
    d_location: str = "CSV",
    league: League = League.EPL,
    environ: str = "development",
) -> pd.DataFrame:
    """Load data from location configured for d_location.

    Parameters
    ----------
    d_location :
        Location to load date from, by default "CSV"
    league :
        League to load data for, by default League.EPL
    environ :
        Weather to load dev or prod data, by default "development"
    """

    def clean_date(d):
        """varying date formats so parse date in consistent format"""
        return parse(d) if isinstance(d, str) else np.nan

    cfg = load_config(environ=environ)  # load configuration

    if d_location not in D_LOCATIONS:
        raise ValueError(
            f"{d_location} is not a valid d_location."
            f"Valid choices: {D_LOCATIONS}."
        )
    if league not in League:
        raise ValueError(
            f"{league} is not a valid league. Valid choices: {League}."
        )

    if d_location == "CSV":
        league_csv = f"{league.value}.csv"
        file_location = pkg_resources.resource_filename(
            __name__, f"data/processed/{league_csv}"
        )
        data = pd.read_csv(file_location, parse_dates=["Time"])
        data["Date"] = data["Date"].apply(clean_date)
    elif d_location == "DATABASE":  # TODO: TO BE COMPLETED LATER
        db_name = cfg.get("DATABASE_NAME")
        # db_host = cfg.get("DATABASE_HOST")
        # db_key = cfg.get("DATABASE_KEY")
        print("DB Name:", db_name)
        # Load data from DB
        # Database extraction to be implemented later
        raise NotImplementedError("Cannot extract data from databases yet...")
    return data


def update_current_season_data(
    league: League, d_location: str = "CSV", persist: bool = False
) -> None:
    """Get the latest data for the season.

    Parameters
    ----------
    league :
        League to get data for
    d_location :
        types of location to persists data, by default "CSV"
    persist : bool, optional
        If True. persists updated data to d_location, by default False

    Raises
    ------
    ValueError
        If an unsupported league is passed
    """
    file_name = f"season_{SEASON}.csv"
    p = pkg_resources.resource_filename(
        __name__, f"data/raw/{league.value}/{file_name}"
    )

    match league:
        case League.EPL:
            url = "https://www.football-data.co.uk/mmz4281/2122/E0.csv"
        case _:
            raise ValueError(f"Unsupported league: {league}")

    season_data = pd.read_csv(url)
    if persist:
        if d_location == "CSV":
            print("Saving/Updating file: ", p)
            season_data.to_csv(p, index=False)
        elif d_location == "DATABASE":
            raise NotImplementedError
    else:
        pprint(season_data)


def read_stitch_raw_data(league: League, persist: bool = False) -> None:
    """Read multiple csv and stitch them together.

    Parameters
    ----------
    league :
        League Type.
    persist :
        If specified, new data file will be saved, by default False
    """

    # concat the files together
    dir_path = Path("data") / "raw" / league.value
    parent_dir = Path(__file__).parent

    print(str(parent_dir / dir_path) + "/season*.csv")
    df = dd.read_csv(
        str(parent_dir / dir_path) + "/season*.csv",
        dtype={"FTAG": "float64", "FTHG": "float64"},
    ).compute()

    if persist:
        file_path = parent_dir / "data" / "processed" / f"{league.value}.csv"
        print(f"Persisting data: {file_path}")
        df.to_csv(file_path)
    print(f"df.shape:\n{df.shape}")
    # print(f"df.sample(frac=0.1):\n{df.sample(frac=0.1)}")


def clean_format_data(X: pd.DataFrame, league: League):
    """Cleans and formats DataFrame.

    Parameters
    ----------
    X:
        Pandas dataframe with soccer statistics
    league:
        Code name of the league
    """
    # -1: Away Team Win
    #  0: Draw
    # +1: Home Team Win
    X = X[
        ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "Date", "Time", "Attendance"]
    ]
    X = X.rename(
        columns={
            "HomeTeam": "home",
            "AwayTeam": "away",
            "FTHG": "home_goal",
            "FTAG": "away_goal",
            "Date": "date",
            "Time": "time",
            "Attendance": "attendance",
        }
    )
    X["date"] = pd.to_datetime(X["date"])
    X = X.dropna(
        subset=["home", "away", "home_goal", "away_goal", "date"], how="all"
    )
    X["time"] = pd.to_datetime(
        X["time"].fillna(method="bfill").fillna(method="ffill")
    )
    X["attendance"] = X["attendance"].fillna(0)
    y = np.sign(X["home_goal"] - X["away_goal"])

    team_code = partial(get_team_code, league.value, code_type="int")
    X["home"] = X["home"].apply(team_code)
    X["away"] = X["away"].apply(team_code)
    # No longer need these columns. This info will not be present at pred
    # TODO: Fix time and date. dropping date and time for now as I cannot seem
    # TODO: to get them working with sklearn and dask at the moment
    X = X.drop(columns=["home_goal", "away_goal", "time", "date"])
    X = X.reset_index(drop=True)

    return X, y


class DataScraper:
    """Data class used to fetch various soccer data from open source."""

    def __init__(self, league: League) -> None:
        self.types = {
            "team_rating": "https://projects.fivethirtyeight.com/soccer-predictions",
            "player_rating": "https://www.whoscored.com/Statistics",
        }  # Dict of data type to scraping url
        self.leagues = {"epl": "premier-league", "bundesliga": "bundesliga"}
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
        last_updated = soup.find("p", {"class": "timestamp"}).get_text()
        last_updated_split = last_updated.split(" ")[1:4]
        d_m_y = (
            last_updated_split[1].strip(",")
            + "/"
            + last_updated_split[0].strip(".").capitalize()
            + "/"
            + last_updated_split[2].strip(",")
        )
        try:  # First try full month name
            last_updated = datetime.strptime(d_m_y, "%j/%B/%Y")
        except ValueError:  # The try 3 letter month name
            try:
                last_updated = datetime.strptime(d_m_y, "%j/%b/%Y")
            except ValueError:
                day, month, year = d_m_y.split("/")
                if month == "Sept":
                    last_updated = datetime(int(year), 9, int(day))
                else:
                    raise
        if type == "team_rating":
            team_ranking = (
                {}
            )  # { teams: {team_name: {overall: <rank>, offense: <rank>, defense: <rank>}, last_updated: 'string' }
            team_ranking["last_updated"] = last_updated
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
            ranking_df = ranking_df.unstack()

        elif type == "player_rating":
            player_ranking = {}
            player_ranking["last_updated"] = last_updated
            raise NotImplementedError
        else:
            raise ValueError(
                f"Invalid scraper type {type}. Valid choices {self.types.keys()}"
            )
        return ranking_df

    def scrape_team_rating(self, persists: bool = False, use_db: bool = False):
        data_type = "team_rating"
        # TODO: Should not be using repeated code like this. use definition above
        leagues = {"epl": "premier-league", "bundesliga": "bundesliga"}
        league_end_point = leagues[self.league.value]
        team_rating_uri = f"{self.types[data_type]}/{league_end_point}/"
        team_ranking_csv = (
            f"data/processed/{self.league.value}_team_ranking.csv"
        )

        print(
            f"Scraping {self.league} '{data_type}' data from {team_rating_uri}"
        )  # TODO: Use _logger instead
        with requests.Session() as session:
            page = session.get(url=team_rating_uri)
        page.raise_for_status()
        print(f"Request status code: {page.status_code}")

        soup = BeautifulSoup(page.content, "html.parser")
        df = self._parse_team_rating_request(soup=soup, type=data_type)
        if persists:
            if use_db:
                raise NotImplementedError
            else:
                print("Updating csv....")
                exist_df = pd.read_csv(
                    pkg_resources.resource_filename(
                        __name__, team_ranking_csv
                    ),
                    index_col=["date", "ranking"],
                    parse_dates=True,
                )
                df = df.stack()
                new_df = pd.concat([exist_df, df], axis=0)
                new_df.to_csv(
                    pkg_resources.resource_filename(__name__, team_ranking_csv)
                )
        else:
            print(
                "Unstacking dataframe for better visibility..."
            )  # TODO: use _logger instead
            pprint(df)
