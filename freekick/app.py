import os
from typing import Optional

from flask import Flask, render_template, url_for
from flask_cors import CORS

from freekick.api import freekick_api
from freekick.learners.learner_utils import compute_cache_all_league_wpc_pyth
from freekick.utils import __version__, _logger
from freekick.utils.freekick_config import load_config


def _init_freekick(
    mode: str, config: dict, init_wpc_pyth: Optional[bool] = None
):
    """Initialize freekick configs."""
    _logger.setLevel(config["LOG_LEVEL"])
    _logger.info(f" Launching FreeKick app in {mode} mode...")
    _logger.info(f"FreeKick Version: {str(__version__)}")
    compute_wpc_pyth = False
    if init_wpc_pyth is not None:
        # If init_wpc_pyth passed, it takes priority, no need to check env
        if init_wpc_pyth:
            compute_wpc_pyth = True
    else:
        compute_wpc_pyth = bool(config.get("INITIALIZE_WPC_PYTH", False))

    if compute_wpc_pyth:
        # Computing Win Percentage and Pythagorean Expectation is very expensive so
        # lets ensure the are initially compted at launch.
        _logger.info("Computing Win Percentage and Pythagorean Expectation...")
        compute_cache_all_league_wpc_pyth()


def create_app(
    mode: Optional[str] = None, init_wpc_pyth: Optional[bool] = None
):
    """Creates FreeKick app"""

    # Create the Flask app
    app = Flask(__name__)
    freekick_api.init_app(app=app)

    # Configure app environment
    mode = mode or os.environ.get("ENV", None)
    if mode:
        config = load_config(environ=mode)
        _init_freekick(mode=mode, config=config, init_wpc_pyth=init_wpc_pyth)
        app.logger.setLevel(config["LOG_LEVEL"])
    else:
        _logger.warning(
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
