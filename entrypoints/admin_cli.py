import logging

import click
from sqlalchemy.orm import Session

from freekick.datastore import DEFAULT_ENGINE
from freekick.datastore.repository import SQLAlchemyRepository
from freekick.datastore.util import DataStore, League
from freekick.learners import DEFAULT_ESTIMATOR
from freekick.learners.learner_utils import train_soccer_model
from freekick.utils import _logger


def list_supported_leagues():
    _logger.info("Learner Options:")
    for model in League:
        _logger.info(f"\t- {model.name}")


@click.command()
@click.option(
    "-r",
    "--retrain",
    help="Retrain model",
    type=click.Choice(League._member_names_, case_sensitive=False),
)
@click.option(
    "-l", "--list-leagues", is_flag=True, help="List supported leagues."
)
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
    default="DATABASE",
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
def cli(retrain, list_leagues, test_size, persist, source, log_level="INFO"):
    _logger.setLevel(log_level)
    if list_leagues:
        list_supported_leagues()
    elif retrain:
        datastore = DataStore[source]
        repo = None
        if datastore.name == DataStore.DATABASE.name:
            session = Session(DEFAULT_ENGINE)
            repo = SQLAlchemyRepository(session)
        train_soccer_model(
            learner=DEFAULT_ESTIMATOR,
            league=League[retrain],
            test_size=test_size,
            datastore=datastore,
            persist=persist,
            repository=repo,
        )


if __name__ == "__main__":
    cli()
