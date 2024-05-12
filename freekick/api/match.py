"""API that calls the match_predictor service"""

from flask import Blueprint, jsonify, request

from freekick.service import predict_match

match_route = Blueprint("match_route", __name__, url_prefix="/api")


@match_route.route("/match", methods=["GET", "POST"])
def match():
    request_data = request.get_json()
    home_team = request_data["home"].replace(" ", "-")
    away_team = request_data["away"].replace(" ", "-")
    league = request_data["league"]
    attendance = request_data["attendance"]
    prediction = predict_match(
        league=league,  # should we create a League enum here or have predict_match create the enum?
        home_team=home_team,
        away_team=away_team,
        attendance=attendance,
    )
    return jsonify(prediction)
