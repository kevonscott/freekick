import logging

import click

from freekick import _logger
from freekick.datastore.util import DataStore, League
from freekick.learners import DEFAULT_ESTIMATOR
from freekick.learners.learner_utils import train_soccer_model


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
@click.option(
    "-m",
    "--log_level",
    help=("Logging level"),
    type=click.Choice(list(logging._levelToName.values())),
    default="INFO",
    show_default=True,
)
def cli(retrain, list, test_size, persist, source, log_level="INFO"):
    _logger.setLevel(log_level)
    if list:
        print("Model Options:")
        for model in League:
            print(f"\t- {model.name}")
    elif retrain:
        train_soccer_model(
            learner=DEFAULT_ESTIMATOR,
            league=League[retrain],
            test_size=test_size,
            datastore=DataStore[source],
            persist=persist,
        )


if __name__ == "__main__":
    cli()
