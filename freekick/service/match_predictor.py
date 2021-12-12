from datetime import datetime
from pprint import pprint
import json

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

from model.ai import serial_models
from model.ai.data_store import load_data


def predict_match(league: str, home_team: str, away_team: str):
    print(league, home_team, away_team)
    home_team = "home_" + home_team
    away_team = "away_" + away_team
    # Load serialized model
    soccer_model = serial_models.get(league.lower())

    now_date = str(datetime.today()).split(" ")[0]
    date_time_now_index = now_date + "_" + home_team + "_" + away_team

    team_name_encoding = OneHotEncoder(sparse=False).fit(
        np.array(soccer_model.columns).reshape(-1, 1)
    )
    home_encoding = team_name_encoding.transform(np.array([home_team]).reshape(-1, 1))
    away_encoding = team_name_encoding.transform(np.array([away_team]).reshape(-1, 1))
    encoding_cols = [t.split("_", 1)[1] for t in team_name_encoding.get_feature_names()]
    single_match = home_encoding + away_encoding
    single_match_df = pd.DataFrame(
        single_match, columns=encoding_cols, index=[date_time_now_index]
    )

    # probability_prediction = soccer_model.predict_probability(single_match_df)
    # prediction = soccer_model.predict_winner(single_match_df)
    pred = soccer_model.predict(single_match_df)

    df_pred = pd.DataFrame(pred, columns=["Prediction"])
    df_pred["Prediction"] = df_pred["Prediction"].apply(
        lambda x: "draw" if x == 0 else ("home_win" if x > 0 else "away_win")
    )
    j_response = json.loads(df_pred.to_json())
    pprint(j_response)
    j_response = {"Prediction": j_response["Prediction"]["0"]}

    return j_response
