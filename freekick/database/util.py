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
    ) -> str | int | None:
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

        code_type:
            Type of code to get. Choices are ['str', 'int']. Default is 'str'.
            Note that if you
        team_code:
            if team code is provided, use team_code instead of team name to get
            int code type
        Returns
        -------
        str | int | None
            Three letter code or integer representing the team. None if team
            cannot  be found.

        Raises
        ------
        ValueError
            Value error if invalid team of league name is provided

        """
        valid_code_types = ("str", "int")
        if code_type not in valid_code_types:
            # Fail early on invalid code_type
            raise ValueError(
                f"Invalid code_type {code_type}. "
                f"Valid options are  {valid_code_types}"
            )
        code: str | int | None = None
        if team_code:
            statement = (
                select(Team)
                .where(Team.code == team_code)
                .where(Team.league == league)
            )
        else:
            statement = (
                select(Team)
                .where(Team.name == team_name)
                .where(Team.league == league)
            )
        entity = repository.session.scalars(statement).one_or_none()
        if not entity:
            pass
        elif code_type == "str":
            code = entity.code
        elif code_type == "int":
            return entity.id

        return code
