from sqlalchemy import select

from freekick.database import DEFAULT_ENGINE
from freekick.database.model import Team

from .repository import AbstractRepository


class DBUtils:
    @staticmethod
    def get_team_code(
        repository: AbstractRepository,
        league: str,
        team_name: str,
        code_type: str = "str",
        team_code: str | None = None,
    ) -> str | int:
        """Looks up a team's code name given its full name.

        Parameters
        ----------
        repository :
            Database abstraction interface to use for db interaction
        league :
            The teams 3 letter code
        team_name :
            Full name of the team

        code_type:
            Type of code to get. Choices are ['str', 'int']. Default is 'str'.
            Note that if you
        team_code:
            if team code is provided, use team_code instead of team name to get
            int code type
        Returns
        -------
        str | int
            Three letter code or integer representing the team.

        Raises
        ------
        ValueError
            Value error if invalid team of league name is provided

        Example
        -------
        >>> from freekick.database import DEFAULT_ENGINE
        >>> from sqlalchemy.orm import Session
        >>> from freekick.database.model import Team
        >>> from freekick.database.repository import SQLAlchemyRepository

        >>> repo = SQLAlchemyRepository(session)
        >>> session = Session(DEFAULT_ENGINE)
        >>> statement =select(Team).where(Team.code=='ARS').where(Team.league=='epl')
        >>> entity = repo.session.scalars(statement).one()
        >>> entity
        Team(code='ARS', name='Arsenal', league='epl')
        >>> entity.id
        1
        >>>
        """
        if team_code:
            statement = (
                select(Team).where(Team.code == team_code).where(Team.league == league)
            )
        else:
            statement = (
                select(Team).where(Team.name == team_name).where(Team.league == league)
            )

        entity = repository.session.sclars(statement).one()
        if code_type == "str":
            try:
                return entity.code
            except KeyError:
                raise ValueError(
                    f"Invalid league ({league}) or team_name ({team_name})"
                )
        elif code_type == "int":
            return entity.id
        else:
            raise ValueError(f"Invalid code_type ({code_type})")
