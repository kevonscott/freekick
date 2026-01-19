from freekick.datastore import get_or_create_session
from freekick.datastore.repository import SQLAlchemyRepository
from freekick.datastore.util import DBUtils, Season

from .util import SeasonDTO


def get_current_season_teams(league: str) -> SeasonDTO:
    """Get list of current season teams.

    :param league: League code
    :return: A SeasonDTO
    """
    repository = SQLAlchemyRepository(get_or_create_session())
    _, teams = DBUtils.get_teams(
        repository=repository, league=league, season=Season.CURRENT
    )
    return SeasonDTO(season=Season.CURRENT.value, teams=teams)
