from typing import Any

import pandas as pd

from freekick.model import League, _logger, get_team_code, serial_models


class PredictorNotFoundError(Exception):
    """Custom exception for unknown learner/model"""

    pass


def predict_match(
    league: str, home_team: str, away_team: str, attendance: int | float
) -> list[dict[str, Any]]:
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
    league: League = League[league.upper()]
    _logger.debug(
        "\n Request Type: Single Match Prediction\n"
        " League\tHome Team\tAway Team\n"
        f" {league}\t{home_team}\t{away_team}"
    )
    # h_team = "home_" + home_team
    # a_team = "away_" + away_team
    # Load serialized model
    home = get_team_code(
        league=league.value, team_name=home_team, code_type="int", team_code=home_team
    )
    away = get_team_code(
        league=league.value, team_name=away_team, code_type="int", team_code=away_team
    )
    try:
        soccer_model = serial_models()[league]
    except KeyError:
        raise PredictorNotFoundError(f"Serial model not found for {league}.")

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
    json_pred = [
        {"Home Team": home_team, "Away Team": away_team, "Predicted Winner": result}
    ]
    _logger.debug(json_pred)
    return json_pred
