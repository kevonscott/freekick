"""API that calls the match_predictor service"""

from flask_restful import Resource, fields, marshal_with, reqparse

from freekick.service import predict_match

resource_fields = {
    "home_team": fields.String,
    "away_team": fields.String,
    "predicted_winner": fields.String,
}

post_parser = reqparse.RequestParser()
post_parser.add_argument("home", type=str, required=True, help="Home team code")
post_parser.add_argument("away", type=str, required=True, help="Away team code")
post_parser.add_argument("league", type=str, required=True, help="league code")
post_parser.add_argument(
    "attendance", type=float, help="Approximate. Average attendance"
)


class Match(Resource):
    @marshal_with(resource_fields)
    def post(self):
        args = post_parser.parse_args(strict=True)
        match_dto = predict_match(
            league=args[
                "league"
            ],  # should we create a League enum here or have predict_match create the enum?
            home_team=args["home"].replace(" ", "-"),
            away_team=args["away"].replace(" ", "-"),
            attendance=args["attendance"],
        )
        return match_dto
