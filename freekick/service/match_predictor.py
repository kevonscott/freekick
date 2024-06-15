import pandas as pd
from sqlalchemy.orm import Session

from freekick import _logger
from freekick.datastore import DATA_UTIL, DEFAULT_ENGINE
from freekick.datastore.repository import SQLAlchemyRepository
from freekick.datastore.util import League
from freekick.learners import serial_models

from .util import MatchDTO

REPOSITORY = SQLAlchemyRepository(Session(DEFAULT_ENGINE))


class LearnerNotFoundError(Exception):
    """Custom exception for unknown learner/model"""

    pass


def predict_match(
    league: str, home_team: str, away_team: str, attendance: int | float
) -> list[MatchDTO]:
    """Predict a single match with using data passed from frontend.

    Prediction is done via the default pre-configured learner/model for each
    league in serial_models.

    Parameters
    ----------
    league :
        League to make prediction in.
    home_team :
        Code of the home team
    away_team :
        code of away team
    attendance :
        Approximate number of attendance

    Returns
    -------
        json results of prediction.
    """
    _league: League = League[league.upper()]
    _logger.info(
        "\n Request Type: Single Match Prediction\n"
        " League\tHomeTeam\tAwayTeam\n"
        f" {league}\t{home_team}\t\t{away_team}"
    )
    # Load serialized model
    # TODO: remove 'home' and 'away' since we are not longer using int team code
    # pass str team codes directly. We will need to retrain the model first.
    home = DATA_UTIL.get_team_code(
        league=_league.value, team_name=home_team, repository=REPOSITORY
    )
    away = DATA_UTIL.get_team_code(
        league=_league.value, team_name=away_team, repository=REPOSITORY
    )
    try:
        soccer_model = serial_models()[_league.value]
    except KeyError:
        raise LearnerNotFoundError(f"Serial model not found for {_league}.")

    # any date will do for index but using the date of the request.
    # selected date will not impact prediction
    # now_date = datetime.today().strftime("%d/%m/%Y")
    # date_time_now_index = now_date + "_" + h_team + "_" + a_team

    # team_name_encoding = OneHotEncoder(sparse=False).fit(
    #     np.array(soccer_model.columns).reshape(-1, 1)
    # )
    # home_encoding = team_name_encoding.transform(np.array([h_team]).reshape(-1, 1))
    # away_encoding = team_name_encoding.transform(np.array([a_team]).reshape(-1, 1))
    # # encoding_cols = [t.split("_", 1)[1] for t in team_name_encoding.get_feature_names()]
    # single_match = home_encoding + away_encoding
    data = {
        "home": [home],
        "away": [away],
        "attendance": [attendance],
    }
    single_match_df = pd.DataFrame(data)

    pred = soccer_model.predict(single_match_df)
    pred = int(pred)
    _logger.debug(f"Prediction: {pred}")
    result = "draw" if pred == 0 else (home_team if pred > 0 else away_team)
    match_dto = [
        MatchDTO(
            home_team=home_team, away_team=away_team, predicted_winner=result
        )
    ]
    _logger.debug(match_dto)
    return match_dto
