from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session

from freekick import _logger
from freekick.datastore import DATA_UTIL, DEFAULT_ENGINE
from freekick.datastore.repository import SQLAlchemyRepository
from freekick.datastore.util import League, Season, season_to_int
from freekick.learners import serial_models
from freekick.learners.learner_utils import add_wpc_pyth

from .util import MatchDTO

REPOSITORY = SQLAlchemyRepository(Session(DEFAULT_ENGINE))


class LearnerNotFoundError(Exception):
    """Custom exception for unknown learner/model"""

    pass


def predict_match(
    league: str,
    home_team: str,
    away_team: str,
    attendance: int | float,
    season: Season = Season.CURRENT,
    match_date: str | None = None,
    time: str | None = None,
) -> list[MatchDTO]:
    """Predict a single match with using data passed from frontend.

    Prediction is done via the default pre-configured learner/model for each
    league in serial_models.

    :param league: League to make prediction in.
    :param home_team: Code of the home team.
    :param away_team: Code of the away team
    :param attendance: Approximate number of attendance
    :param season: Season Code, defaults to Season.CURRENT
    :param match_date: Date the game is played, defaults to None
    :param time: Time the game is played, defaults to None
    :raises LearnerNotFoundError: _description_
    :return: Results of prediction.
    :rtype: list[MatchDTO]
    """
    _league: League = League[league.upper()]
    _logger.info(
        "\n Request Type: Single Match Prediction\n"
        " League\tHomeTeam\tAwayTeam\n"
        f" {league}\t{home_team}\t\t{away_team}"
    )
    # pass str team codes directly. We will need to retrain the model first.
    # home = DATA_UTIL.get_team_code(
    #     league=_league.value, team_name=home_team, repository=REPOSITORY
    # )
    # away = DATA_UTIL.get_team_code(
    #     league=_league.value, team_name=away_team, repository=REPOSITORY
    # )
    home_id = DATA_UTIL.get_team_id(team_code=home_team)
    away_id = DATA_UTIL.get_team_id(team_code=away_team)
    try:
        # Load serialized model
        soccer_model = serial_models()[_league.value]
    except KeyError:
        raise LearnerNotFoundError(f"Serial model not found for {_league}.")

    data = {
        "date": (
            [pd.Timestamp(match_date)]
            if match_date
            else [pd.Timestamp(datetime.now().date())]
        ),
        "time": [pd.to_datetime(time)] if time else [pd.to_datetime("1:00")],
        "home_team": [home_id],
        "away_team": [away_id],
        "season": [season_to_int(season)],
        "attendance": [attendance],
    }
    single_match_df = pd.DataFrame(data).astype(
        {
            "date": "int64",
            "time": "int64",
            "home_team": "category",
            "away_team": "category",
            "season": "category",
        }
    )
    single_match_df = add_wpc_pyth(
        data=single_match_df, league=League[league.upper()], season=season
    )
    pred = soccer_model.predict(single_match_df)
    _logger.debug(f"Prediction: {pred}")
    pred = int(pred)
    result = "Draw" if pred == 0 else (home_team if pred > 0 else away_team)
    match_dto = [
        MatchDTO(
            home_team=home_team, away_team=away_team, predicted_winner=result
        )
    ]
    _logger.debug(match_dto)
    return match_dto
