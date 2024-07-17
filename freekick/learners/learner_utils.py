"""Model for all Machine Learning Operations."""

import pickle
from datetime import datetime
from functools import lru_cache, partial
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from freekick import ESTIMATOR_LOCATION, _logger
from freekick.datastore.util import (
    DataStore,
    League,
    Season,
    get_league_data_container,
    season_to_int,
)

from .classification import BaseClassifier


def _load_model(model_name: str):
    """Load and deserialize a model."""
    model_path = ESTIMATOR_LOCATION / model_name
    with open(model_path, "rb") as plk_file:
        model = pickle.load(plk_file)  # noqa B301
        _logger.debug(f"     - {model_name}")
    return model


TRAINING_COLS = [
    "date",
    "time",
    "home_team",
    "away_team",
    "season",
    "attendance",
    "home_win_percentage",
    "away_win_percentage",
    "home_pyth_expectation",
    "away_pyth_expectation",
]


@lru_cache()
def load_models() -> dict[str, Any]:
    _logger.debug(" Loading serialized models...")
    return {
        league.value: _load_model(model_name=f"{league.value}.pkl")
        for league in League
    }


serial_models = partial(load_models)


# ===============
def compute_wpc_pyth(data):
    """Compute win percentage and pythagorean expectation for home and away teams."""
    # We first identify whether the result was a win for the home team (H),
    # the away team (A) or a draw (D). We also create the counting variable.
    data["game_count"] = 1  # represent # games played in each season
    # home_win=1, draw=0.5,away_win=0
    data["home_win_value"] = np.where(
        data["result"] == "H", 1, np.where(data["result"] == "D", 0.5, 0)
    )
    # Away win=1, draw=0.5,home_win=0
    data["away_win_value"] = np.where(
        data["result"] == "A", 1, np.where(data["result"] == "D", 0.5, 0)
    )

    # We have to create separate dfs to calculate home team and away
    # team performance.
    home = (
        data.groupby(["season", "home_team"])[
            ["game_count", "home_win_value", "home_goal", "away_goal"]
        ]
        .sum()
        .reset_index()
        .rename(
            columns={
                "home_team": "team",
                "game_count": "game_count_home",
                "home_goal": "home_goal_home",
                "away_goal": "away_goal_home",
            }
        )
    )

    # Now we create the mirror image df for the away team results.
    away = (
        data.groupby(["season", "away_team"])[
            ["game_count", "away_win_value", "home_goal", "away_goal"]
        ]
        .sum()
        .reset_index()
        .rename(
            columns={
                "away_team": "team",
                "game_count": "game_count_away",
                "home_goal": "home_goal_away",
                "away_goal": "away_goal_away",
            }
        )
    )

    # Merge the home team and away team results
    home_away = pd.merge(home, away, on=["season", "team"])

    # Sum the results by home and away measures to get the team overall
    # performance for the season
    home_away["wins"] = (
        home_away["home_win_value"] + home_away["away_win_value"]
    )
    home_away["game_count"] = (
        home_away["game_count_home"] + home_away["game_count_away"]
    )
    home_away["goals_for"] = (
        home_away["home_goal_home"] + home_away["away_goal_away"]
    )
    home_away["goals_against"] = (
        home_away["away_goal_home"] + home_away["home_goal_away"]
    )

    home_away = home_away.set_index(["season", "team"])

    # Create the win percentage and pythagorean expectation
    home_away["win_percentage"] = home_away["wins"] / home_away["game_count"]
    home_away["pyth_expectation"] = home_away["goals_for"] ** 2 / (
        home_away["goals_for"] ** 2 + home_away["goals_against"] ** 2
    )

    def _get_wpc(season, team, perf=home_away):
        return perf.loc[(season, team)]["win_percentage"]

    def _get_pyth(season, team, perf=home_away):
        return perf.loc[(season, team)]["pyth_expectation"]

    data["home_win_percentage"] = data.apply(
        lambda row: _get_wpc(row["season"], row["home_team"]), axis=1
    )
    data["away_win_percentage"] = data.apply(
        lambda row: _get_wpc(row["season"], row["away_team"]), axis=1
    )

    data["home_pyth_expectation"] = data.apply(
        lambda row: _get_pyth(row["season"], row["home_team"]), axis=1
    )
    data["away_pyth_expectation"] = data.apply(
        lambda row: _get_pyth(row["season"], row["away_team"]), axis=1
    )

    data = data.drop(
        columns=["game_count", "home_win_value", "away_win_value"]
    )
    return data


def train_soccer_model(
    learner: BaseClassifier,
    league: League,
    test_size: float,
    datastore: DataStore = DataStore.DEFAULT,
    persist: bool = False,
):
    _logger.info(f"Retraining {league}...")
    league_container = get_league_data_container(league=league.value)(
        datastore=datastore
    )
    X = league_container.load()
    X = compute_wpc_pyth(X)
    y = X["result"].astype("category")
    X = X.drop(columns=["result", "home_goal", "away_goal"])
    X = X.astype(
        {
            "date": "int64",
            "time": "int64",
            "home_team": "category",
            "away_team": "category",
            "season": "category",
        }
    )
    X = X[TRAINING_COLS]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size  # Time series data so need to stratify
    )
    soccer_model = learner(league=league)
    soccer_model.fit(X=X_train, y=y_train)  # train/fit the model
    y_pred = soccer_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    # coeff = soccer_model.get_coeff()
    print("=========================Model Statistics=========================")
    print(f"Model Type: {soccer_model.model}")
    print(f"Model Name: {soccer_model.name}")
    print(f"Accuracy: {accuracy}")
    # print("Coeff:")
    # pprint(coeff)

    if persist:
        soccer_model.persist_model()


def add_wpc_pyth(
    data: pd.DataFrame,
    league: League,
    season: Season = Season.CURRENT,
    datastore: DataStore = DataStore.DEFAULT,
):
    """Add wpc and pyth for each team in data"""
    league_container = get_league_data_container(league=league.value)(
        datastore=datastore
    )
    X = league_container.load()
    # Filter current season data
    X = X[X["season"] == season_to_int(season)]
    X = compute_wpc_pyth(
        X
    )  # TODO: this is expensive and should be cached!! Also compute at launch
    away_team_wpc_pyth = (
        X[["away_team", "away_win_percentage", "away_pyth_expectation"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    home_team_wpc_pyth = (
        X[["home_team", "home_win_percentage", "home_pyth_expectation"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    data = pd.merge(data, away_team_wpc_pyth, on="away_team")
    data = pd.merge(data, home_team_wpc_pyth, on="home_team")

    return data[TRAINING_COLS]  # reorder cols to match training


if __name__ == "__main__":
    d = {
        "date": [pd.Timestamp(datetime.now().date())],
        "time": [pd.to_datetime("1:00")],
        "home_team": [2077942607848583336],
        "away_team": [9132668287013610014],
        "attendance": [0.0],
        "season": [season_to_int(Season.CURRENT)],
    }
    data = pd.DataFrame(d).astype(
        {
            "date": "int64",
            "time": "int64",
            "home_team": "category",
            "away_team": "category",
            "season": "category",
        }
    )
    add_wpc_pyth(data=data, league=League.EPL)
