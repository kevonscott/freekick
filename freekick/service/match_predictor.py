from datetime import datetime
from pprint import pprint
from typing import Union

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

from freekick.model.ai import serial_models, _logger, get_team_code


def predict_match(
    league: str, home_team: str, away_team: str, attendance: Union[int, float]
):
    _logger.debug(
        "\n Request Type: Single Match Prediction\n"
        " League\tHome Team\tAway Team\n"
        f" {league}\t{home_team}\t{away_team}"
    )
    # h_team = "home_" + home_team
    # a_team = "away_" + away_team
    # Load serialized model
    home = get_team_code(
        league=league, team_name=home_team, code_type="int", team_code=home_team
    )
    away = get_team_code(
        league=league, team_name=away_team, code_type="int", team_code=away_team
    )
    soccer_model = serial_models().get(league.lower())

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
