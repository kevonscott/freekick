from pprint import pprint

import click
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from freekick import _logger
from freekick.datastore.util import (
    DataStore,
    League,
    get_league_data_container,
)
from freekick.learners import SoccerLogisticModel


# TODO: Move train_soccer_model to a classmethod withing the model and call
# into it. Otherwise we will need to replicate this code once we start adding
# more models and have front end specifying which model/predictor it wants to use.
def train_soccer_model(
    model_name: League,
    test_size: float,
    source: str = "CSV",
    persist: bool = False,
):
    _logger.info(f"Retraining {model_name}...")
    league_container = get_league_data_container(league=model_name.value)(
        datastore=DataStore.DEFAULT
    )
    X = league_container.load()
    X, y = league_container.clean_format_data(X)
    # X = load_data(d_location=source, league=model_name)
    # X, y = clean_format_data(X=X, league=model_name)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size  # Time series data so need to stratify
    )
    soccer_model = SoccerLogisticModel(model_name.value, X_train, y_train)
    soccer_model.fit()  # train/fit the model
    # soccer_model.model.columns = list(X.columns)

    y_pred = soccer_model.predict_winner(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    coeff = soccer_model.get_coeff()
    print("=========================Model Statistics=========================")
    print(f"Model: {soccer_model.model}")
    print(f"Accuracy: {accuracy}")
    print("Coeff:")
    pprint(coeff)

    if persist:
        soccer_model.persist_model()


@click.command()
@click.option(
    "-r",
    "--retrain",
    help="Retrain model",
    type=click.Choice(League._member_names_, case_sensitive=False),
)
@click.option("-l", "--list", is_flag=True, help="List current models")
@click.option(
    "-p",
    "--persist",
    is_flag=True,
    help="Serialize model to disk if provided.",
)
@click.option(
    "-t",
    "--test_size",
    default=0.2,
    help="Training Size.",
    type=float,
    show_default=True,
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
def cli(retrain, list, test_size, persist, source):
    if list:
        print("Model Options:")
        for model in League:
            print(f"\t- {model.name}")
    elif retrain:
        train_soccer_model(
            model_name=League[retrain],
            test_size=test_size,
            source=source,
            persist=persist,
        )


if __name__ == "__main__":
    cli()
