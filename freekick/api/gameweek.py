from flask_restx import Namespace, Resource, fields, reqparse

from freekick.service import predict_match_day

gameweek_ns = Namespace("gameweek", description="Game week operations.")
gameweek_model = gameweek_ns.model(
    "GameWeek",
    {
        "home_team": fields.String,
        "away_team": fields.String,
        "predicted_winner": fields.String,
    },
)

post_parser = reqparse.RequestParser()
post_parser.add_argument("league", type=str, required=True, help="league code")


@gameweek_ns.route("/")
class MatchDayApi(Resource):
    @gameweek_ns.doc("predict_gameweek")
    @gameweek_ns.marshal_with(gameweek_model)
    @gameweek_ns.expect(post_parser)
    def post(self):
        args = post_parser.parse_args(strict=True)
        match_day_dto = predict_match_day(league=args["league"])
        return match_day_dto
