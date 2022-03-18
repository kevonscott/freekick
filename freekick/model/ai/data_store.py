import requests
import pkg_resources
from pathlib import Path
from pprint import pprint
from datetime import datetime

import pandas as pd
import dask.dataframe as dd
from bs4 import BeautifulSoup

from utils.freekick_config import load_config
from model.ai import _LEAGUES, _SEASON


def load_data(d_location="CSV", league="bundesliga", environ="development"):
    cfg = load_config(environ=environ)  # load configuration

    d_locations = ["CSV", "DATABASE"]
    if d_location not in d_locations:
        raise ValueError(
            f"{d_location} is not a valid d_location. Please select from {d_locations}."
        )
    if league not in _LEAGUES:
        raise ValueError(
            f"{league} is not a valid league. Please select from {_LEAGUES}."
        )

    if d_location == "CSV":
        league_csv = f"{league}.csv"
        file_location = pkg_resources.resource_filename(
            __name__, f"data/processed/{league_csv}"
        )
        data = pd.read_csv(file_location)
    elif d_location == "DATABASE":  # TO BE COMPLETED LATER
        db_name = cfg.get("DATABASE_NAME")
        # db_host = cfg.get("DATABASE_HOST")
        # db_key = cfg.get("DATABASE_KEY")
        print("DB Name:", db_name)
        # Load data from DB
        # Database extraction to be implemented later
        raise NotImplementedError("Cannot extract data from databases yet...")

    return data


def update_current_season_data(league, d_location="CSV", persist=False):
    file_name = f"season_{_SEASON}.csv"
    p = pkg_resources.resource_filename(__name__, f"data/raw/{league}/{file_name}")
    if league == "epl":
        url = "https://www.football-data.co.uk/mmz4281/2122/E0.csv"

    if url:
        season_data = pd.read_csv(url)
        if persist:
            if d_location == "CSV":
                print("Saving/Updating file: ", p)
            elif d_location == "DATABASE":
                raise NotImplementedError
            season_data.to_csv(p, index=False)
        else:
            pprint(season_data)
    else:
        raise ValueError(f"Unsupported league: {league}")


def read_stitch_raw_data(league, persist=False):
    """Read multiple csv and stitch them together.

    Parameters
    ----------
    league : str
        Name of the league.
    persist : bool, optional
        If specified, new data file will be saved, by default False
    """
    if league not in _LEAGUES:
        raise ValueError(f"Invalid League. Please select from {_LEAGUES}")

    def _read_csv(csv_path):
        print(f"Extracting data from: {csv_path}")
        return pd.read_csv(csv_path)

    # concat the files together
    dir_path = Path("data") / "raw" / league
    parent_dir = Path(__file__).parent
    # data_files = pkg_resources.resource_listdir(__name__, str(dir_path))
    # data_files = [parent_dir / dir_path / f for f in data_files]

    # df = pd.concat(map(_read_csv, data_files), ignore_index=True)
    print(str(parent_dir / dir_path) + "/season*.csv")
    df = dd.read_csv(
        str(parent_dir / dir_path) + "/season*.csv",
        dtype={"FTAG": "float64", "FTHG": "float64"},
    ).compute()

    if persist:
        file_path = parent_dir / "data" / "processed" / f"{league}.csv"
        print(f"Persisting data: {file_path}")
        df.to_csv(file_path)
    # print(f"df.shape:\n{df.shape}")
    # print(f"df.sample(frac=0.1):\n{df.sample(frac=0.1)}")


class DataScraper:
    """Data class used to fetch various soccer data from open source."""

    def __init__(self, league) -> None:
        self.types = {
            "team_rating": "https://projects.fivethirtyeight.com/soccer-predictions",
            "player_rating": "https://www.whoscored.com/Statistics",
        }  # Dict of data type to scraping url
        self.leagues = {"epl": "premier-league", "bundesliga": "bundesliga"}
        self.league = league

    def _parse_team_rating_request(self, soup, type):
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
        last_updated = datetime.strptime(d_m_y, "%j/%B/%Y")
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

        elif self.type == "player_rating":
            player_ranking = {}
            player_ranking["last_updated"] = last_updated
            raise NotImplementedError
        else:
            raise ValueError(
                f"Invalid scraper type {type}. Select from {self.types.keys()}"
            )
        return ranking_df

    def scrape_team_rating(self, persists=False, use_db=False):
        data_type = "team_rating"
        leagues = {"epl": "premier-league", "bundesliga": "bundesliga"}
        league_end_point = leagues[self.league]
        team_rating_uri = f"{self.types[data_type]}/{league_end_point}/"
        team_ranking_csv = f"data/processed/{self.league}_team_ranking.csv"

        print(f"Scraping {self.league} '{data_type}' data from {team_rating_uri}")
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
                    pkg_resources.resource_filename(__name__, team_ranking_csv),
                    index_col=["date", "ranking"],
                    parse_dates=True,
                )
                df = df.stack()
                new_df = pd.concat([exist_df, df], axis=0)
                new_df.to_csv(
                    pkg_resources.resource_filename(__name__, team_ranking_csv)
                )
        else:
            print("Unstacking dataframe for better visibility...")
            pprint(df)
