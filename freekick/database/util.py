from sqlalchemy import select

from freekick.database.model import Game, Team
from freekick.model.ai import Season

from .repository import AbstractRepository


class TeamNotFoundError(Exception):
    pass


class DBUtils:
    @staticmethod
    def get_team_code(
        repository: AbstractRepository,
        league: str,
        team_name: str,
    ) -> str:
        """Looks up a team's integer or string code name given its full name or
        team_code.

        Parameters
        ----------
        repository :
            Database abstraction interface to use for db interaction
        league :
            The teams 3 letter code
        team_name :
            Full name of the team
        Returns
        -------
        str
            Three letter code or integer representing the team. None if team
            cannot  be found.

        Raises
        ------
        TeamNotFoundError
            Value error if invalid team or not found.

        """
        statement = (
            select(Team)
            .where(Team.name == team_name)
            .where(Team.league == league)
        )
        entity = repository.session.scalars(statement).one_or_none()
        if not entity:
            raise TeamNotFoundError(f"Team code not found for '{team_name}'.")

        return entity.code

    @staticmethod
    def get_teams(
        repository: AbstractRepository,
        league: str,
        season: Season,
    ) -> tuple[str, dict]:
        statement = (
            select(Team)
            .join(Game, Game.home_team == Team.code)
            .where(Game.league == league)
            .where(Game.season == season.value)
        )
        entities = repository.session.scalars(statement).all()
        teams: dict = {}
        for entity in entities:
            if entity.code not in teams:
                teams[entity.code] = entity.name
        return season.value, teams
