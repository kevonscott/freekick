"""Utility module for all Machine Learning Operations."""

import time
from functools import lru_cache, partial
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from freekick import ESTIMATOR_LOCATION
from freekick.datastore import DEFAULT_REPOSITORY
from freekick.datastore.util import (
    DataStore,
    League,
    Season,
    get_league_data_container,
    season_to_int,
)
from freekick.utils import Timer, _logger

from .classification import BaseClassifier

WPC_PYTH_CACHE: dict[str, pd.DataFrame | float] = {
    "league": {},
    "last_update": None,
}
WPC_PYTH_CACHE_EXPIRE_SECONDS: int = 86400  # 1 day

pd.options.mode.copy_on_write = True  # Enable copy and write.


def _load_model(model_name: str):
    """Load and deserialize a model."""
    model_path = ESTIMATOR_LOCATION / model_name
    model = joblib.load(model_path)
    _logger.debug(f"     - {model_name}")
    return model


TRAINING_COLS = [
    "date",
    "day_of_week",
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


def compute_wpc_pyth(data: pd.DataFrame, league: League) -> pd.DataFrame:
    """Compute win percentage and pythagorean expectation for home and away teams."""
    # TODO: this is expensive and currently being cached at startup!! Consider compute and push to db since db for faster access
    # or store in DB, but for now, lets cache in WPC_PYTH_CACHE variable
    global WPC_PYTH_CACHE
    last_update = WPC_PYTH_CACHE.get("last_update")
    if (
        last_update
        and (league.value in WPC_PYTH_CACHE.get("league", {}))
        and ((time.time() - last_update) < WPC_PYTH_CACHE_EXPIRE_SECONDS)
    ):
        print("cache hit, returning....")
        return WPC_PYTH_CACHE["league"][league.value]
    print("cache miss, recomputing wpc-pyth....")
    # We first identify whether the result was a win for the home team (H),
    # the away team (A) or a draw (D). We also create the counting variable.
    data["game_count"] = 1  # represent # games played in each season
    # home_win=1, draw=0.5,away_win=0
    data["home_win_value"] = np.where(
        data["result"] == 1, 1, np.where(data["result"] == 0, 0.5, 0)
    )
    # Away win=1, draw=0.5,home_win=0
    data["away_win_value"] = np.where(
        data["result"] == -1, 1, np.where(data["result"] == 0, 0.5, 0)
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
        columns=[
            "game_count",
            "home_win_value",
            "away_win_value",
            "home_goal",
            "away_goal",
        ]
    )
    WPC_PYTH_CACHE["league"][league.value] = data
    WPC_PYTH_CACHE["last_update"] = time.time()
    return data


def train_soccer_model(
    learner: BaseClassifier,
    league: League,
    test_size: float,
    datastore: DataStore = DataStore.DEFAULT,
    persist: bool = False,
):
    _logger.info(f"Retraining predictive model for {league}...")
    league_container = get_league_data_container(league=league.value)(
        datastore=datastore
    )
    X = league_container.load()
    X = compute_wpc_pyth(data=X, league=league)
    y = X["result"].astype("category")
    X = X.drop(columns=["result"])
    X = X.astype(
        {
            "date": "int64",
            "day_of_week": "category",
            "time": "int64",
            "home_team": "category",
            "away_team": "category",
            "season": "category",
        }
    )
    X = X[TRAINING_COLS]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
    )
    soccer_model = learner(league=league)
    soccer_model.fit(X=X_train, y=y_train)  # train/fit the model
    y_pred = soccer_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    _logger.info("==================Model Statistics=========================")
    _logger.info(f"Model Type: {soccer_model.model}")
    _logger.info(f"Model Name: {soccer_model.name}")
    _logger.info(f"Accuracy: {accuracy}")

    if persist:
        soccer_model.persist_model()


def add_wpc_pyth(
    data: pd.DataFrame,
    league: League,
    season: Season = Season.CURRENT,
    datastore: DataStore = DataStore.DEFAULT,
    repository=None,
):
    """Add wpc and pyth for each team in data"""
    league_container = get_league_data_container(league=league.value)(
        datastore=datastore,
        repository=repository,
    )
    cached_wpc_pyth = league.value in WPC_PYTH_CACHE.get("league", {})
    if cached_wpc_pyth:
        X = WPC_PYTH_CACHE["league"][league.value]
        X = X[X["season"] == season_to_int(season)]
    else:
        X = league_container.load()
        # Filter current season data
        X = X[X["season"] == season_to_int(season)]
        X = compute_wpc_pyth(data=X, league=league)
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


def compute_cache_all_league_wpc_pyth(
    datastore: DataStore = DataStore.DEFAULT,
):
    for league in League:
        with Timer():
            league_container = get_league_data_container(league=league.value)(
                datastore=datastore, repository=DEFAULT_REPOSITORY
            )
            X = league_container.load()
            X[X["season"] == season_to_int(Season.CURRENT)]
            compute_wpc_pyth(data=X, league=league)
