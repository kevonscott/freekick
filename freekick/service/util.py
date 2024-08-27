"""Data Transfer Objects (DTO) for sending across network.
"""

import threading
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd

from freekick import _logger
from freekick.datastore.util import League, TeamName
from freekick.learners import serial_models
from freekick.learners.learner_utils import (
    WPC_PYTH_CACHE,
    WPC_PYTH_CACHE_EXPIRE_SECONDS,
    compute_cache_all_league_wpc_pyth,
)


@dataclass
class MatchDTO:
    home_team: str
    away_team: str
    predicted_winner: str


class SeasonDTO:
    def __init__(self, season: str, teams: list[TeamName]) -> None:
        self.season = season
        self.teams = teams


class LearnerNotFoundError(Exception):
    """Custom exception for unknown learner/model"""

    pass


def _predict(data: pd.DataFrame, league: League) -> np.ndarray:
    time_now = time.time()
    last_update = WPC_PYTH_CACHE.get("last_update")
    time_elapsed = time_now - (last_update or 0.0)
    if not last_update or (time_elapsed > WPC_PYTH_CACHE_EXPIRE_SECONDS):
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
        raise LearnerNotFoundError(f"Serial model not found for {league}.")

    return soccer_model.predict(data)
