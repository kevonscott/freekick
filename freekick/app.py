from flask import Flask, render_template
from flask_cors import CORS

# Blueprints
from api.match_day import match_day_route
from api.match import match_route


def create_app():
    app = Flask(__name__)
    app.register_blueprint(match_day_route)
    app.register_blueprint(match_route)
    CORS(app)

    @app.route("/")
    @app.route("/home")
    def welcome():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
