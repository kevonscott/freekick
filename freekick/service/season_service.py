from sqlalchemy.orm import Session

from freekick.database import DEFAULT_ENGINE
from freekick.database.repository import SQLAlchemyRepository
from freekick.database.util import DBUtils
from freekick.model.ai import Season

from .util import SeasonDTO


def get_current_season_teams(league: str):
    repository = SQLAlchemyRepository(Session(DEFAULT_ENGINE))
    _, teams = DBUtils.get_teams(
        repository=repository, league=league, season=Season.CURRENT
    )
    return SeasonDTO(season=Season.CURRENT.value, teams=teams)
