from flask_restx import Namespace, Resource, fields

from freekick.service import get_current_season_teams

season_ns = Namespace("season", description="Season operations")
team_model = season_ns.model(
    "Team", {"code": fields.String, "name": fields.String}
)
season_model = season_ns.model(
    "Season",
    {"season": fields.String, "teams": fields.List(fields.Nested(team_model))},
)


@season_ns.route("/<league>")
@season_ns.param("league", "League Code")
class SeasonApi(Resource):
    @season_ns.marshal_with(season_model)
    def get(self, league):
        """Query the current season list of teams for a league."""
        season_dto = get_current_season_teams(league=league)
        return season_dto, 200
