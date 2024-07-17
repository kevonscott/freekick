"""API that calls the match_predictor service"""

from flask_restx import Namespace, Resource, fields, reqparse

from freekick.service import predict_match

match_ns = Namespace("match", description="Single match operations.")
match_model = match_ns.model(
    "Match",
    {
        "home_team": fields.String,
        "away_team": fields.String,
        "predicted_winner": fields.String,
    },
)

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    "home_team", type=str, required=True, help="Home team code"
)
post_parser.add_argument(
    "away_team", type=str, required=True, help="Away team code"
)
post_parser.add_argument("league", type=str, required=True, help="League code")
post_parser.add_argument(
    "attendance", type=float, help="Approximate attendance"
)


@match_ns.route("/")
class MatchApi(Resource):
    @match_ns.doc("predict_match")
    @match_ns.marshal_with(match_model)
    @match_ns.expect(post_parser)
    def post(self):
        args = post_parser.parse_args(strict=True)
        # TODO: Also get date and time from front ends request and pass to
        # predict_match
        match_dto = predict_match(
            # TODO should inherit and use League enum here or have
            # predict_match create the enum?
            league=args["league"],
            home_team=args["home_team"].replace(" ", "-"),
            away_team=args["away_team"].replace(" ", "-"),
            attendance=args["attendance"],
        )
        return match_dto
