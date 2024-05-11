from flask import Flask, render_template
from flask_cors import CORS

from freekick.api.match import match_route
from freekick.api.match_day import match_day_route


def create_app():
    """Creates FreeKick app"""

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
