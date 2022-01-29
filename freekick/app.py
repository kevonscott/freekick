#! env/bin/python

import sys
import click
import logging


logging.basicConfig()
_logger = logging.getLogger("FreeKick")
_logger.setLevel(logging.INFO)

sys.path.append(".")


def create_app():
    """Creates FreeKick app"""
    from flask import Flask, render_template  # noqa E402
    from flask_cors import CORS  # noqa E402

    # Blueprints
    from freekick.api.match_day import match_day_route  # noqa E402
    from freekick.api.match import match_route  # noqa E402

    app = Flask(__name__)
    app.register_blueprint(match_day_route)
    app.register_blueprint(match_route)
    CORS(app)

    @app.route("/")
    @app.route("/home")
    def welcome():
        return render_template("index.html")

    return app


@click.command()
@click.option(
    "-e",
    "--env",
    help="Environment to run in",
    type=click.Choice(["PROD", "DEV"], case_sensitive=False),
    default="DEV",
    show_default=True,
)
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
def main(env, logging_level):
    _logger.setLevel(logging_level.upper())
    _logger.info(f" Launching FreeKick app in {env} mode....")

    app = create_app()
    if env.upper() == "DEV":
        app.run(debug=True)
    else:
        app.run()


if __name__ == "__main__":
    main()
