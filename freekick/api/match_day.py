from flask import Blueprint, jsonify, request

from service.match_day_predictor import predict_match_day

match_day_route = Blueprint("match_day_route", __name__, url_prefix="/api")


@match_day_route.route("/matchday", methods=["GET", "POST"])
def matchday():
    request_data = request.get_json()
    # home_team = request_data['home']
    # away_team = request_data['away']
    league = request_data["league"]
    prediction = predict_match_day(league=league)
    return jsonify(prediction)
