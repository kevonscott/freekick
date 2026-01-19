"""Model for generating data for training our models"""

import click
# from sqlalchemy.orm import Session

from freekick.datastore import get_or_create_session
from freekick.datastore.repository import SQLAlchemyRepository
from freekick.datastore.util import (
    CSVUtils,
    DataScraper,
    DataStore,
    DBUtils,
    League,
    get_league_data_container,
)
from freekick.learners.learner_utils import update_wpc_pyth
from freekick.utils import _logger

UPDATE_TYPES = [
    "team_rating",
    "player_rating",
    "match",
    "current_season",
    "wpc_pyth",
]
_logger.setLevel("INFO")


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "-d",
    "--data-type",
    help=("The type of data to update"),
    type=click.Choice(UPDATE_TYPES, case_sensitive=True),
    required=True,
)
@click.option(
    "-l",
    "--league",
    help="Target league to update.",
    type=click.Choice(League._member_names_, case_sensitive=False),
    required=True,
)
@click.option(
    "-p", "--persist", is_flag=True, help="Save updated date to disk."
)
@click.option(
    "-e",
    "--env",
    help="Environment.",
    type=click.Choice(["DEV", "PROD", "TEST"], case_sensitive=False),
    required=True,
)
def update(data_type, league, persist):
    match data_type:
        case "player_rating":
            raise NotImplementedError
        case "team_rating":
            data_scraper = DataScraper(league=League[league])
            data_scraper.scrape_team_rating(persists=persist)
        case "match":
            raise NotImplementedError
            # Read in new data and override the current file if persist == True
            # read_stitch_raw_data(league=League[league], persist=persist)
            # league_container.read_stitch_raw_data(league=league, persist=persist)
        case "current_season":
            league_container = get_league_data_container(league=league)
            session = get_or_create_session()
            repo = SQLAlchemyRepository(session)
            for store in DataStore:
                league_data = league_container(
                    datastore=store, repository=repo
                )
                league_data.update_current_season(persist=persist)
        case "wpc_pyth":
            update_wpc_pyth(league=League[league], persist=True, cache=True)
        case _:
            raise ValueError(
                "Invalid data_type. Please select from %s", UPDATE_TYPES
            )


@click.command()
@click.option(
    "-l", "--list", help="List currently supported leagues.", is_flag=True
)
def league(list):
    if list:
        print(League._member_names_)


@click.command()
@click.argument("name")
@click.argument("code")
@click.argument("league")
def add_team(name, code, league):
    teams = [
        DBUtils.new_team(team_code=code, team_name=name, league=League[league])
    ]
    session = get_or_create_session()
    repo = SQLAlchemyRepository(session)
    DBUtils.add_teams(teams=teams, repository=repo)
    CSVUtils.add_teams(teams=teams)


cli.add_command(update)
cli.add_command(league)
cli.add_command(add_team)

if __name__ == "__main__":
    cli()
