from pprint import pprint

import click

from freekick.app import create_app  # noqa E402
from freekick.service import predict_match  # noqa E402
from freekick.utils import __version__, _logger  # noqa E402


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option(
    "-l",
    "--logging-level",
    help="Logging level",
    type=click.Choice(
        ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"], case_sensitive=False
    ),
    default="INFO",
    show_default=True,
)
@click.option(
    "-e",
    "--env",
    help="Environment to run in",
    type=click.Choice(["PROD", "DEV"], case_sensitive=False),
    default="DEV",
    show_default=True,
)
@click.pass_context
def cli(ctx, debug, env, logging_level):
    ctx.ensure_object(dict)
    if debug:
        logging_level = "DEBUG"
    _logger.setLevel(logging_level)
    ctx.obj["LOGGING_LEVEL"] = logging_level
    ctx.obj["ENV"] = env


@cli.command()
@click.option(
    "--league", "-l", required=True, help="Football/Soccer league code", type=str
)
@click.option(
    "--home", "-r", required=True, help="Home team code league code", type=str
)
@click.option(
    "--away", "-a", required=True, help="Away team code league code", type=str
)
@click.option(
    "--attendance",
    "-g",
    help="Estimated attendance of the game",
    type=float,
    default=0.0,
)
@click.pass_context
def match(ctx, league, home, away, attendance):
    """Predict the head to head clash between two teams within a league."""
    prediction = predict_match(
        league=league, home_team=home, away_team=away, attendance=attendance
    )
    pprint(prediction[0])


@cli.command()
@click.option("--league", "-l", required=True, help="Football/Soccer league code")
@click.pass_context
def season(ctx, league):
    """Predict all the games within a league."""
    raise NotImplementedError("Sorry, I cannot predict seasons as yet!")


@cli.command()
@click.option(
    "--port", "-p", help="Web port to open for webapp", default=39592, type=int
)
@click.pass_context
def serve(ctx, port):
    env = ctx.obj["ENV"]
    _logger.info(f" Launching FreeKick app in {env} mode....")
    _logger.info(f"FreeKick Version: {str(__version__)}")

    app = create_app()
    app.logger.setLevel(ctx.obj["LOGGING_LEVEL"])
    if env.upper() == "DEV":
        app.run(debug=True, port=port)
    else:
        app.run(port=port)


if __name__ == "__main__":
    cli()
