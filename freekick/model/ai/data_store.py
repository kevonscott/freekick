import pandas as pd
from pathlib import Path
import pkg_resources

from utils.freekick_config import load_config
from model.ai import _LEAGUES


def load_data(d_location="CSV", league="bundesliga", environ="development"):
    cfg = load_config(environ=environ)  # load configuration

    d_locations = ["CSV", "DATABASE"]
    if d_location not in d_locations:
        raise KeyError(
            f"{d_location} is not a valid d_location. Please select from {d_locations}."
        )
    if league not in _LEAGUES:
        raise KeyError(
            f"{league} is not a valid league. Please select from {_LEAGUES}."
        )

    if d_location == "CSV":
        league_csv = league + ".csv"
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


def update_current_season_data(league):
    raise NotImplementedError


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
    data_files = pkg_resources.resource_listdir(__name__, str(dir_path))
    data_files = [parent_dir / dir_path / f for f in data_files]

    df = pd.concat(map(_read_csv, data_files), ignore_index=True)

    if persist:
        file_path = parent_dir / "data" / "processed" / f"{league}.csv"
        print(f"Persisting data: {file_path}")
        df.to_csv(file_path)
    print(f"df.sample():\n{df.sample(5)}")
