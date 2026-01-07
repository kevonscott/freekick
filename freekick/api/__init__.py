from flask_restx import Api

from freekick.utils import __version__

from .gameweek import gameweek_ns
from .healthcheck import HealthCheckApi
from .match import match_ns
from .season import season_ns
from .settings import setting_ns

freekick_api = Api(
    title="Freekick",
    version=str(__version__),
    prefix="/api",
    validate=True,
    doc="/swagger",
)

freekick_api.add_namespace(match_ns)
freekick_api.add_namespace(gameweek_ns)
freekick_api.add_namespace(season_ns)
freekick_api.add_namespace(setting_ns)
freekick_api.add_resource(HealthCheckApi, "/health")
