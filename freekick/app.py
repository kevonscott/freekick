from flask import Flask, render_template
from flask_cors import CORS

from freekick.api import freekick_api


def create_app():
    """Creates FreeKick app"""

    app = Flask(
        __name__,
    )
    freekick_api.init_app(app=app)

    CORS(app)

    @app.route("/")
    @app.route("/home")
    def welcome():
        return render_template("index.html")

    return app
