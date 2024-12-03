"""Utility module for all Machine Learning Operations."""

import os
from datetime import datetime
from functools import lru_cache, partial
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from freekick import ESTIMATOR_LOCATION
from freekick.datastore import DEFAULT_REPOSITORY
from freekick.datastore.repository import AbstractRepository
from freekick.datastore.util import (
    DataStore,
    League,
    Season,
    get_league_data_container,
    season_to_int,
)
from freekick.utils import Timer, _logger
from freekick.utils.freekick_config import coerce_env_dir_name

from .classification import BaseClassifier, FreekickDecisionTreeClassifier
from .regression import SoccerLogisticModel


# Container for all active estimators/forecasters.
AllEstimator = {
    "FreekickDecisionTreeClassifier": FreekickDecisionTreeClassifier,
    "SoccerLogisticModel": SoccerLogisticModel,
}
DEFAULT_ESTIMATOR = AllEstimator["FreekickDecisionTreeClassifier"]


# This cache is ONLY used for caching the WPC and PYTH values for current season
# (Season.CURRENT) teams so we do not have to compute or query DB for each
# prediction. e.g. {'epl': {'data': pd.DataFrame, 'last_update': datetime}}
WPC_PYTH_CACHE: dict[str, dict[str, pd.DataFrame | datetime]] = {}
WPC_PYTH_CACHE_TIMEOUT: pd.Timedelta = pd.Timedelta(days=1)  # 86400s/1day

pd.options.mode.copy_on_write = True  # Enable copy and write.


def _load_model(league: League) -> Any:
    """Load and deserialize a model."""
    env = os.environ["ENV"]
    estimator_cls_name = os.environ.get(f"{league.name}_ESTIMATOR_CLASS")
    if not estimator_cls_name:
        _logger.warning(
            (
                "Environment estimator not specified for %s!!! Falling "
                "back to loading 'DEFAULT_ESTIMATOR': %s"
            ),
            league.name,
            DEFAULT_ESTIMATOR,
        )
        estimator_cls_name = DEFAULT_ESTIMATOR.__name__
    env_subdir = coerce_env_dir_name(env_name=env)
    model_name = f"{league.value}_{estimator_cls_name}.pkl"
    model_path = ESTIMATOR_LOCATION / env_subdir / model_name
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
    "home_pythagorean_expectation",
    "away_pythagorean_expectation",
]


@lru_cache()
def load_models() -> dict[str, Any]:
    _logger.debug(" Loading serialized models...")
    return {league.value: _load_model(league=league) for league in League}


serial_models = partial(load_models)


def compute_wpc_pyth(
    data: pd.DataFrame, league: League, cache: bool = False
) -> pd.DataFrame:
    """Compute win percentage and pythagorean expectation for home and away teams."""
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

    def _get_wpc(
        season: str, team: str, perf: pd.DataFrame = home_away
    ) -> pd.Series:  # type: ignore [type-arg]
        return perf.loc[(season, team)]["win_percentage"]  # type: ignore

    def _get_pyth(
        season: str, team: str, perf: pd.DataFrame = home_away
    ) -> pd.Series:  # type: ignore [type-arg]
        return perf.loc[(season, team)]["pyth_expectation"]  # type: ignore

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

    data["pyth_wpc_id"] = (
        data["home_team"].astype(str) + "_" + data["season"].astype(str)
    )
    if set(data.home_team) ^ set(data.away_team):
        raise ValueError(
            "Some teams are in away_team and not home_team or vice-verse. Cannot compute wpc_pyth"
        )
    data = data[
        [
            "home_team",
            "season",
            "home_win_percentage",
            "home_pyth_expectation",
            "pyth_wpc_id",
        ]
    ]
    data = data.rename(
        {
            "home_team": "team",
            "home_win_percentage": "win_percentage",
            "home_pyth_expectation": "pythagorean_expectation",
        },
        axis="columns",
    )
    data["league"] = league.value
    data = data.drop_duplicates(subset="team")

    now = datetime.now()
    data["last_update"] = now
    if cache:
        global WPC_PYTH_CACHE
        WPC_PYTH_CACHE[league.value] = {
            "data": data,
            "last_update": now,
        }
    return data


def train_soccer_model(
    learner: type[BaseClassifier],
    league: League,
    test_size: float,
    env: str,
    datastore: DataStore = DataStore.DEFAULT,
    persist: bool = False,
    repository: Optional[AbstractRepository] = None,
) -> None:
    _logger.info(f"Retraining predictive model for {league}...")
    league_container = get_league_data_container(league=league.value)(
        datastore=datastore, repository=repository
    )  # type: ignore [call-arg]
    X = league_container.load()
    X = add_wpc_pyth(
        data=X,
        league=league,
        datastore=datastore,
        season=None,  # Very Important we specify, season=None
        repository=repository,
    )
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
        soccer_model.persist_model(env=env)


def load_wpc_pyth(league: League) -> pd.DataFrame | None:
    if league.value in WPC_PYTH_CACHE:
        last_update = WPC_PYTH_CACHE.get(league.value, {}).get(
            "last_update", pd.Timestamp.min
        )
        if (datetime.now() - last_update) < WPC_PYTH_CACHE_TIMEOUT:
            _logger.info("WPC_PYTH cache hit....")
            return WPC_PYTH_CACHE[league.value]["data"]  # type: ignore [return-value]
        else:
            _logger.warning(
                "cache miss for wpc-pyth, trying persistent storage...."
            )
            # Try loading from storage TODO
            # if fail or does not exists, return None
            _logger.warning("Storage WPC PYTH not yet implemented...")
            _logger.warning("WPC PYTH storage lookup miss....")

    return None


def add_wpc_pyth(
    data: pd.DataFrame,
    league: League,
    season: Optional[Season] = Season.CURRENT,
    datastore: DataStore = DataStore.DEFAULT,
    repository: Optional[AbstractRepository] = None,
) -> pd.DataFrame:
    """Add win percentage (wpc) and pythagorean expectation (pyth) for each team

    :param data: DataFrame to add win percentage and pythagorean expectation to
    :param league: The league to operate in
    :param season: Season to operate within, defaults to Season.CURRENT
                    if none, compute for all season in dataset, 'season' col
                    must exist.
    :param datastore: datastore to use, defaults to DataStore.DEFAULT.
    :param repository: repository to use, defaults to None
    :raises ValueError: when unsupported season is passed.
    :return: Result with wpc and pyth columns added
    """
    if season not in {Season.CURRENT, None}:
        raise ValueError(
            "Only current season or all seasons are supported when adding "
            f"wpc and pyth, received {season}"
        )

    if season:
        cached_wpc_pyth = load_wpc_pyth(league=league)
        if (
            isinstance(cached_wpc_pyth, pd.DataFrame)
            and not cached_wpc_pyth.empty
        ):
            X = cached_wpc_pyth[
                cached_wpc_pyth["season"] == season_to_int(season)
            ]
        else:
            league_container = get_league_data_container(league=league.value)(
                datastore=datastore,
                repository=repository,
            )  # type: ignore [call-arg]
            X = league_container.load()
            # Filter current season data
            X = X[X["season"] == season_to_int(season)]
            X = compute_wpc_pyth(data=X, league=league, cache=True)
    else:
        # For all other season, there are no caching so we need to recompute
        # every time. This should only be needed during training so we should
        # not see any performance impact for live predictions.
        league_container = get_league_data_container(league=league.value)(
            datastore=datastore,
            repository=repository,
        )  # type: ignore [call-arg]
        X = league_container.load()
        X = compute_wpc_pyth(data=X, league=league, cache=False)
    X = X[["team", "season", "win_percentage", "pythagorean_expectation"]]

    away_team_wpc_pyth = X.rename(
        columns={
            "team": "away_team",
            "win_percentage": "away_win_percentage",
            "pythagorean_expectation": "away_pythagorean_expectation",
        }
    )
    home_team_wpc_pyth = X.rename(
        columns={
            "team": "home_team",
            "win_percentage": "home_win_percentage",
            "pythagorean_expectation": "home_pythagorean_expectation",
        }
    )

    data = pd.merge(
        data, away_team_wpc_pyth, how="left", on=["away_team", "season"]
    )
    data = pd.merge(
        data, home_team_wpc_pyth, how="left", on=["home_team", "season"]
    )
    return data


def compute_cache_all_league_wpc_pyth(
    datastore: DataStore = DataStore.DEFAULT,
) -> None:
    # Compute and cache wpc_pyth but do not persists to disk/database.
    for league in League:
        with Timer():
            update_wpc_pyth(
                league=league, datastore=datastore, persist=False, cache=True
            )


def update_wpc_pyth(
    league: League,
    datastore: Optional[DataStore] = None,
    persist: bool = False,
    cache: bool = False,
) -> None:
    """Update win percentage and pythagorean expectation in persistent storage.

    :param league: League for which to update
    :param datastore: Persistent storage for which to update, defaults to None.
                    If None or not provided, update for all DataStore
    """
    league_container = get_league_data_container(league=league.value)(
        datastore=datastore or DataStore.DEFAULT, repository=DEFAULT_REPOSITORY
    )  # type: ignore [call-arg]
    X = league_container.load()
    X = X[X["season"] == season_to_int(Season.CURRENT)]
    wpc_pyth = compute_wpc_pyth(data=X, league=league, cache=cache)
    if persist:
        # Persists to permanent store
        datastores = [datastore] if datastore else list(DataStore)
        for ds in datastores:
            ds.value().add_or_update_wpc_pyth(
                data=wpc_pyth, league=league, repository=DEFAULT_REPOSITORY
            )
