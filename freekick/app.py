import os
from typing import Optional

from flask import Flask, render_template
from flask_cors import CORS

from freekick.api import freekick_api
from freekick.learners.learner_utils import compute_cache_all_league_wpc_pyth
from freekick.utils import __version__, _logger
from freekick.utils.freekick_config import load_config


def _init_freekick(mode: str, config: dict):
    """Initialize freekick configs."""
    _logger.setLevel(config["LOG_LEVEL"])
    _logger.info(f" Launching FreeKick app in {mode} mode...")
    _logger.info(f"FreeKick Version: {str(__version__)}")
    init_wpc_pyth = bool(config.get("INITIALIZE_WPC_PYTH", False))
    if init_wpc_pyth:
        # Computing Win Percentage and Pythagorean Expectation is very expensive so
        # lets ensure the are initially compted at launch.
        _logger.info("Computing Win Percentage and Pythagorean Expectation...")
        compute_cache_all_league_wpc_pyth()


def create_app(env: Optional[str] = None, init_wpc_pyth=True):
    """Creates FreeKick app"""

    # Create the Flask app
    app = Flask(__name__)
    freekick_api.init_app(app=app)

    # Configure app environment
    mode = env or os.environ.get("ENV", None)
    if mode:
        config = load_config(environ=mode)
        _init_freekick(mode, config)
        app.logger.setLevel(config["LOG_LEVEL"])
    else:
        _logger.warn(
            "Environment not specified! Please define 'ENV' environment"
            " variable. Skipping app configuration..."
        )

    CORS(app)

    @app.route("/")
    @app.route("/home")
    def welcome():
        return render_template("index.html")

    return app


app = create_app()
