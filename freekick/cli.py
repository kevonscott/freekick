#! env/bin/python

import click
from pprint import pprint

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from model.ai import soccer_teams, _MODELS
from model.ai.data_store import load_data
from model.ai.models.logistic_model import SoccerLogisticModel


def train_soccer_model(model_name, test_size, source="CSV", persist=False):
    model_score = {}
    print(f"Retraining {model_name}...")

    def _clean_format_data(X):
        """Cleans and formats dataframe

        Parameters
        ----------
        X: Dataframe
            Pandas dataframe with soccer statistics
        """
        # -1: Away Team Win
        #  0: Draw
        # +1: Home Team Win
        X = X[["HomeTeam", "AwayTeam", "FTHG", "FTAG", "Date"]]
        X = X.rename(
            columns={
                "HomeTeam": "home",
                "AwayTeam": "away",
                "FTHG": "home_goals",
                "FTAG": "away_goals",
                "Date": "date",
            }
        )
        X = X.dropna()
        y = np.sign(X["home_goals"] - X["away_goals"])
        X["home"] = X["home"].apply(lambda x: soccer_teams[model_name][x])
        X["away"] = X["away"].apply(lambda x: soccer_teams[model_name][x])
        X.index = X["date"] + "_" + X["home"] + "_" + X["away"]

        # No longer need these columns. This info will not be present at pred
        X = X.drop(columns=["home_goals", "away_goals", "date"])

        X = pd.get_dummies(
            X, columns=["home", "away"], prefix=["home", "away"]
        )  # create dummies (OneHotEncoding) from each team name
        X = X[
            sorted(X.columns)
        ]  # Sort columns to match OneHotEncoding below (VERY IMPORTANT)
        return X, y

    X = load_data(d_location=source, league=model_name)
    X, y = _clean_format_data(X=X)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y
    )

    soccer_model = SoccerLogisticModel(model_name, X_train, y_train)
    soccer_model.fit()  # train/fit the model
    soccer_model.model.columns = list(X.columns)

    y_pred = soccer_model.predict_winner(X_test)
    model_score["accuracy"] = accuracy_score(y_test, y_pred)
    # model_score['coeff'] = soccer_model.get_coeff()
    print("Model Statistics:")
    pprint(model_score)
    print(f"Model: {soccer_model.model}")

    if persist:
        soccer_model.persist_model()


@click.command()
@click.option(
    "-r",
    "--retrain",
    help="Retrain model",
    type=click.Choice(_MODELS, case_sensitive=False),
)
@click.option("-l", "--list", is_flag=True, help="List current models")
@click.option(
    "-p", "--persist", is_flag=True, help="Serialize model to disk if provided."
)
@click.option(
    "-s", "--size", default=0.2, help="Training Size.", type=float, show_default=True
)
@click.option(
    "-s",
    "--source",
    help=(
        "Source of the training data. Default is CSV. If CSV, place the csv"
        " data file with the same name as the model in the data directory"
    ),
    type=click.Choice(["CSV", "DATABASE"]),
    default="CSV",
    show_default=True,
)
def cli(retrain, list, size, persist, source):
    if list:
        print("Model Options:")
        for model in _MODELS:
            print(f"\t- {model}")
    elif retrain:
        train_soccer_model(
            model_name=retrain, test_size=size, source=source, persist=persist
        )


if __name__ == "__main__":
    cli()
