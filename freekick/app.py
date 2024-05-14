from flask import Flask, render_template
from flask_cors import CORS
from flask_restful import Api

from freekick.api.healthcheck import HealthCheck
from freekick.api.match import Match
from freekick.api.match_day import MatchDay


def create_app():
    """Creates FreeKick app"""

    app = Flask(
        __name__,
    )
    api = Api(app=app, prefix="/api")
    api.add_resource(Match, "/match")
    api.add_resource(MatchDay, "/matchday")
    api.add_resource(HealthCheck, "/healthy")

    CORS(app)

    @app.route("/")
    @app.route("/home")
    def welcome():
        return render_template("index.html")

    return app
