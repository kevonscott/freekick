from pprint import pprint

from flask_restful import Resource, fields, marshal_with, reqparse

from freekick.service import get_current_season_teams

resource_fields = {
    "season": fields.String,
    "teams": fields.Raw,
}

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    "league", type=str, required=True, help="League Code."
)


class SeasonApi(Resource):
    @marshal_with(resource_fields)
    def post(self):
        """Query the current season list of teams for a league."""
        args = post_parser.parse_args(strict=True)
        league = args["league"]
        season_dto = get_current_season_teams(league=league)
        pprint(season_dto)
        return season_dto, 200
