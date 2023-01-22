#! .venv/bin/python

import sys

# import click


sys.path.append(".")

from freekick import __version__, _logger  # noqa E402


def create_app():
    """Creates FreeKick app"""
    from flask import Flask, render_template  # noqa E402
    from flask_cors import CORS  # noqa E402

    # Blueprints
    from freekick.api.match_day import match_day_route  # noqa E402
    from freekick.api.match import match_route  # noqa E402

    app = Flask(
        __name__,
    )
    app.register_blueprint(match_day_route)
    app.register_blueprint(match_route)
    CORS(app)

    @app.route("/")
    @app.route("/home")
    def welcome():
        return render_template("index.html")

    return app
