#! venv/bin/python

"""Model for generating datafiles used for each model"""

import click

from model.ai import _LEAGUES, _SEASON
from model.ai.data_store import (
    read_stitch_raw_data,
    DataScraper,
    update_current_season_data,
)

UPDATE_TYPES = ["team_rating", "player_rating", "match", "current_season"]


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "-d",
    "--data-type",
    help=("The type of data to update"),
    type=click.Choice(UPDATE_TYPES, case_sensitive=False),
    required=True,
)
@click.option(
    "-l",
    "--league",
    help="Target league to update.",
    type=click.Choice(_LEAGUES, case_sensitive=False),
    required=True,
)
@click.option("-p", "--persist", is_flag=True, help="Save updated date to disk.")
def update(data_type, league, persist):
    if data_type == "player_rating":
        raise NotImplementedError
    elif data_type == "team_rating":
        data_scraper = DataScraper(league=league)
        data_scraper.scrape_team_rating(persists=persist)
    elif data_type == "match":
        # raise NotImplementedError
        # Read in new data and override the current file if persist == True
        read_stitch_raw_data(league=league, persist=persist)
    elif data_type == "current_season":
        update_current_season_data(league=league, persist=persist)


@click.command()
@click.option("-l", "--list", help="List currently supported leagues.", is_flag=True)
def league(list):
    if list:
        print(_LEAGUES)


cli.add_command(update)
cli.add_command(league)

if __name__ == "__main__":
    cli()
