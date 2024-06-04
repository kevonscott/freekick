from flask_restful import Resource, fields, marshal_with, reqparse

from freekick.service import predict_match_day

resource_fields = {
    "home_team": fields.String,
    "away_team": fields.String,
    "predicted_winner": fields.String,
}

post_parser = reqparse.RequestParser()
post_parser.add_argument("league", type=str, required=True, help="league code")


class MatchDayApi(Resource):
    @marshal_with(resource_fields)
    def post(self):
        args = post_parser.parse_args(strict=True)
        match_day_dto = predict_match_day(league=args["league"])
        return match_day_dto
