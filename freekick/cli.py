import click
from pprint import pprint

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from model.ai.data_store import load_data
from model.ai.models.logistic_model import SoccerLogisticModel

_MODELS = ["epl", "bundesliga"]


def train_soccer_model(model_name, test_size, source="CSV", persist=False):
    model_score = {}
    print(f"Retraining {model_name}...")

    def _clean_format_data(data):
        """Cleans and formats dataframe

        Parameters
        ----------
        data : Dataframe
            Pandas dataframe with soccer statistics
        """
        # -1: Away Team Win
        #  0: Draw
        # +1: Home Team Win
        data = data[["HomeTeam", "AwayTeam", "FTHG", "FTAG", "Date"]]
        data = data.rename(
            columns={
                "HomeTeam": "home",
                "AwayTeam": "away",
                "FTHG": "home_goals",
                "FTAG": "away_goals",
                "Date": "date",
            }
        )
        data = data.dropna()
        y = np.sign(data["home_goals"] - data["away_goals"])
        # breakpoint()
        data["home"] = data["home"].apply(lambda x: x.replace(" ", "-"))
        data["away"] = data["away"].apply(lambda x: x.replace(" ", "-"))
        data.index = data["date"] + "_" + data["home"] + "_" + data["away"]

        # No longer need these columns. This info will not be present at pred
        data = data.drop(columns=["home_goals", "away_goals", "date"])

        data = pd.get_dummies(
            data, columns=["home", "away"], prefix=["home", "away"]
        )  # create dummies (OneHotEncoding) from each team name
        data = data[
            sorted(data.columns)
        ]  # Sort columns to match OneHotEncoding below (VERY IMPORTANT)
        return data, y

    data = load_data(d_location=source, league=model_name)
    X, y = _clean_format_data(data=data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

    soccer_model = SoccerLogisticModel(model_name, X_train, y_train)
    soccer_model.fit()  # train/fit the model
    soccer_model.model.columns = list(X.columns)

    y_pred = soccer_model.predict_winner(X_test)
    model_score["accuracy"] = accuracy_score(y_test, y_pred)
    # model_score['coeffs'] = soccer_model.get_coeff()
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
            print(f"\t{model}")
    elif retrain:
        train_soccer_model(
            model_name=retrain, test_size=size, source=source, persist=persist
        )


if __name__ == "__main__":
    cli()
