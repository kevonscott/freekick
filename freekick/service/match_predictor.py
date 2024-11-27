from datetime import datetime

import pandas as pd

from freekick.datastore import DATA_UTIL, DEFAULT_REPOSITORY
from freekick.datastore.util import League, Season, season_to_int
from freekick.learners.learner_utils import add_wpc_pyth
from freekick.utils import _logger

from .util import MatchDTO, _predict

REPOSITORY = DEFAULT_REPOSITORY


def predict_match(
    league: str | League,
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
    :return: Results of prediction.
    :rtype: list[MatchDTO]
    """
    if isinstance(league, str):
        league = League[league.upper()]
    _logger.info(
        "Request Type: Single Match Prediction\n"
        " League\t\tHomeTeam\tAwayTeam\tTime\tDate\n"
        f" {league}\t{home_team}\t\t{away_team}\t\t{time}\t{match_date}\n"
    )

    home_id = DATA_UTIL.get_team_id(team_code=home_team, repository=REPOSITORY)
    away_id = DATA_UTIL.get_team_id(team_code=away_team, repository=REPOSITORY)

    date = (
        pd.Timestamp(match_date)
        if match_date
        else pd.Timestamp(datetime.now().date())
    )
    data = {
        "date": [date],
        "day_of_week": date.day_of_week,
        "time": [pd.to_datetime(time)] if time else [pd.to_datetime("13:30")],
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
        data=single_match_df,
        league=league,
        season=season,
        repository=REPOSITORY,
    )
    pred = _predict(single_match_df, league=league)
    _logger.debug(f"Prediction: {pred}")
    result_int: int = int(pred[0])
    result = (
        "Draw"
        if result_int == 0
        else (home_team if result_int > 0 else away_team)
    )
    match_dto = [
        MatchDTO(
            home_team=home_team, away_team=away_team, predicted_winner=result
        )
    ]
    _logger.debug(match_dto)
    return match_dto
