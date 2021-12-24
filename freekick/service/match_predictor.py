from datetime import datetime
from pprint import pprint

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

from model.ai import serial_models
from model.ai import _logger


def predict_match(league: str, home_team: str, away_team: str):
    _logger.info(
        "\n Request Type: Single Match Prediction\n"
        " League\tHome Team\tAway Team\n"
        f" {league}\t{home_team}\t{away_team}"
    )
    h_team = "home_" + home_team
    a_team = "away_" + away_team
    # Load serialized model
    soccer_model = serial_models.get(league.lower())

    # any date will do for index but using the date of the request.
    # selected date will not impact prediction
    now_date = datetime.today().strftime("%d/%m/%Y")
    date_time_now_index = now_date + "_" + h_team + "_" + a_team

    team_name_encoding = OneHotEncoder(sparse=False).fit(
        np.array(soccer_model.columns).reshape(-1, 1)
    )
    home_encoding = team_name_encoding.transform(np.array([h_team]).reshape(-1, 1))
    away_encoding = team_name_encoding.transform(np.array([a_team]).reshape(-1, 1))
    encoding_cols = [t.split("_", 1)[1] for t in team_name_encoding.get_feature_names()]
    single_match = home_encoding + away_encoding
    single_match_df = pd.DataFrame(
        single_match, columns=encoding_cols, index=[date_time_now_index]
    )

    pred = soccer_model.predict(single_match_df)
    pred = int(pred)
    _logger.info(f"Prediction: {pred}")
    result = "draw" if pred == 0 else (home_team if pred > 0 else away_team)
    json_pred = [
        {"Home Team": home_team, "Away Team": away_team, "Predicted Winner": result}
    ]
    pprint(json_pred)
    return json_pred
