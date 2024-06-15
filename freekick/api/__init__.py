# TODO: API requests also take arg which specify which model/learner is wants
# to use. Will be needed once we have more than one model at a time. This will
# make it easier to switch out models at any time.
from flask_restx import Api

from freekick import __version__

from .gameweek import gameweek_ns
from .healthcheck import HealthCheckApi
from .match import match_ns
from .season import season_ns

freekick_api = Api(
    title="Freekick", version=str(__version__), prefix="/api", validate=True
)

freekick_api.add_namespace(match_ns)
freekick_api.add_namespace(gameweek_ns)
freekick_api.add_namespace(season_ns)
freekick_api.add_resource(HealthCheckApi, "/health")
