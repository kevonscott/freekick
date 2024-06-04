from flask import Flask, render_template
from flask_cors import CORS
from flask_restful import Api

from freekick.api.healthcheck import HealthCheckApi
from freekick.api.match import MatchApi
from freekick.api.match_day import MatchDayApi
from freekick.api.season import SeasonApi


def create_app():
    """Creates FreeKick app"""

    app = Flask(
        __name__,
    )
    api = Api(app=app, prefix="/api")
    api.add_resource(MatchApi, "/match")
    api.add_resource(MatchDayApi, "/matchday")
    api.add_resource(HealthCheckApi, "/healthy")
    api.add_resource(SeasonApi, "/season")

    CORS(app)

    @app.route("/")
    @app.route("/home")
    def welcome():
        return render_template("index.html")

    return app
