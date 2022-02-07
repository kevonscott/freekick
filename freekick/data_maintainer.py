#! env/bin/python

"""Model for generating datafiles used for each model"""

import click

from model.ai.data_store import read_stitch_raw_data
from model.ai import _MODELS


@click.command()
@click.option(
    "-m",
    "--model",
    help=(
        "Model for which to re-generate data file. Create a single file in freekick/freekick/model/ai/data/processed for model training. Run once new data file is added to "
        "freekick/freekick/model/ai/data/raw folder"
    ),
    type=click.Choice(_MODELS, case_sensitive=False),
)
@click.option("-p", "--persist", is_flag=True, help="Save updated date to disk.")
def cli(model, persist):
    # Read in new data and override the current file if persist == True
    read_stitch_raw_data(model=model, persist=persist)


if __name__ == "__main__":
    cli()
