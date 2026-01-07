"""Data Transfer Objects (DTO) for sending across network."""

import threading
from dataclasses import dataclass

import numpy as np
import pandas as pd

from freekick.datastore.util import League, TeamName
from freekick.learners import serial_models
from freekick.learners.learner_utils import (
    TRAINING_COLS,
    WPC_PYTH_CACHE,
    WPC_PYTH_CACHE_TIMEOUT,
    compute_cache_all_league_wpc_pyth,
)
from freekick.utils import _logger


@dataclass
class MatchDTO:
    home_team: str
    away_team: str
    predicted_winner: str


class SeasonDTO:
    def __init__(self, season: str, teams: list[TeamName]) -> None:
        self.season = season
        self.teams = teams

@dataclass
class SettingDTO:
    estimator: dict[str, str]
    default_league: str
    models: list[str]

class LearnerNotFoundError(Exception):
    """Custom exception for unknown learner/model"""

    pass


def _predict(data: pd.DataFrame, league: League) -> np.ndarray[np.float64]:  # type: ignore
    """Predict the result of a game(s).

    :param data: Input data
    :param league: League to make a prediction for.
    :raises LearnerNotFoundError: Raised when no learner found for league.
    :return: Array with same length as data. A forecast for each data entry.
    :rtype: np.ndarray
    """
    time_now = pd.Timestamp.now()
    last_update = pd.Timestamp(WPC_PYTH_CACHE.get("last_update"))  # type: ignore
    time_elapsed = time_now - (last_update or pd.Timestamp.min)
    if not last_update or (time_elapsed > WPC_PYTH_CACHE_TIMEOUT):
        # Kick off a background thread to update WPC_PYTH_CACHE
        # Note we are not blocking on the completion of this update
        thread = threading.Thread(target=compute_cache_all_league_wpc_pyth)
        thread.start()
        _logger.info(
            " Started thread to update WPC_PYTH_CACHE: "
            f"{thread.name} ({thread.ident})"
        )

    try:
        # Load serialized model
        soccer_model = serial_models()[league.value]
    except KeyError:
        raise LearnerNotFoundError(
            f"Serial model not found for {league}."
        ) from None
    data = data[TRAINING_COLS]  # reorder cols to match training
    return soccer_model.predict(data)  # type: ignore [no-any-return]
