# import numpy as np

# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score

# # from sklearn.preprocessing import OneHotEncoder
# # import pickle
# # import os
# # import sys

# from data_store import load_data
# from models.logistic_model import SoccerLogisticModel


# def create_fit_model(X_train, y_train):
#     """Create and return the trained/fitted soccer model.

#     Parameters
#     ----------
#     X_train : DataFrame
#         X training data
#     y_train : DataFrame
#         y training data

#     Returns
#     -------
#     SoccerLogisticModel
#         A soccer logistics model
#     """
#     model = SoccerLogisticModel(X_train, y_train)
#     model.fit()  # train/fit the model
#     return model


# def clean_format_data(data):
#     """Cleans and formats dataframe

#     Parameters
#     ----------
#     data : Dataframe
#         Pandas dataframe with soccer statistics
#     """
#     # -1: Away Team Win
#     #  0: Draw
#     # +1: Home Team Win
#     y = np.sign(data["home_goals"] - data["away_goals"])
#     data["home"] = data["home"].apply(lambda x: x.replace(" ", "-"))
#     data["away"] = data["away"].apply(lambda x: x.replace(" ", "-"))
#     data.index = data["date"] + "_" + data["home"] + "_" + data["away"]

#     # No longer need these colums. This info will not be present at pred
#     data = data.drop(columns=["home_goals", "away_goals", "date"])

#     data = pd.get_dummies(
#         data, columns=["home", "away"], prefix=["home", "away"]
#     )  # create dummies (OneHotEncoding) from each team name
#     data = data[
#         sorted(data.columns)
#     ]  # Sort colums to match OneHotEncoding below (VERY IMPORTANT)
#     return data, y


# # def persist_model(model, name='soccer_model'):
# #     """Persists a model as Pickle file on disk in models folder. Overrite if
# #     file alredy exists.

# #     Parameters
# #     ----------
# #     model : SoccerLogisticModel
# #         Logistics regression model
# #     name : str, optional
# #         Name of the pickle file, by default 'soccer_model'
# #     """
# #     path_path = os.path.abspath(os.path.join('models', name +'.pkl'))
# #     with open(path_path, 'wb+') as mod_file:
# #         pickle.dump(model, mod_file)


# def main():
#     test_size = 0.2
#     # Import dataset for respective league
#     data = load_data(d_location="CSV", league="EPL")
#     X, y = clean_format_data(data=data)
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

#     model = create_fit_model(X_train, y_train)
#     # persist_model(model=model, name='soccer_model')
#     # model.persist_model()
#     # Create data to represent a single game for prediction
#     # now_date = str(datetime.today()).split(' ')[0]
#     # date_time_now_index = now_date+'_'+'Everton'+'_'+'Tottenham Hotspur'
#     # team_name_encoding = OneHotEncoder(
#     #       sparse=False).fit(data.columns.values.reshape(-1,1)
#     # )

#     # everton_encoding = team_name_encoding.transform(
#     #       np.array(['home_Everton']).reshape(-1,1)
#     # )
#     # tot_encoding = team_name_encoding.transform(
#     #       np.array(['away_Tottenham Hotspur']).reshape(-1,1)
#     # )
#     # encoding_cols = [
#     #   t.split('_',1)[1] for t in team_name_encoding.get_feature_names()
#     # ]
#     # single_match = everton_encoding + tot_encoding
#     # single_match_df = pd.DataFrame(
#     #       single_match, columns=encoding_cols, index=[date_time_now_index]
#     # )

#     # probability_prediction = model.predict_probability(single_match_df)
#     y_prob = model.predict_probability(X_test)
#     print("Win probability:\n", y_prob)
#     print("\n\n")

#     y_pred = model.predict_winner(X_test)
#     model_accuracy = accuracy_score(y_test, y_pred)
#     model_score = model.model.score(X_test, y_test)
#     print(f"Model Accuracy: {model_accuracy}")
#     print(f"Model Score: {model_score}")


# if __name__ == "__main__":
#     main()
