"""API that calls the match_predictor service"""
from flask import Blueprint, jsonify, request

from freekick.service.match_predictor import predict_match

match_route = Blueprint("match_route", __name__, url_prefix="/api")


@match_route.route("/match", methods=["GET", "POST"])
def match():
    request_data = request.get_json()
    home_team = request_data["home"].replace(" ", "-")
    away_team = request_data["away"].replace(" ", "-")
    league = request_data["league"]
    prediction = predict_match(league=league, home_team=home_team, away_team=away_team)
    return jsonify(prediction)
