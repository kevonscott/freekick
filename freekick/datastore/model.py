import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

STRING_LENGTH = 50


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    home_team: Mapped[str] = mapped_column(ForeignKey("team.code"))
    away_team: Mapped[str] = mapped_column(ForeignKey("team.code"))
    home_goal: Mapped[int]
    away_goal: Mapped[int]
    season: Mapped[Optional[str]]
    league: Mapped[str]
    date: Mapped[datetime.date]
    time: Mapped[Optional[str]]
    attendance: Mapped[Optional[float]]
    result: Mapped[str]

    def __repr__(self) -> str:
        return (
            f"Game(home_team={self.home_team!r}, away_team={self.away_team!r}, "
            f"home_gaol={self.home_goal!r}, away_gaol={self.away_goal!r}, "
            f"season={self.season!r}), "
            f"league={self.league!r}, date={self.date!r}, time={self.time!r} "
            f"attendance={self.attendance!r}"
        )


class Team(Base):
    __tablename__ = "team"

    code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(STRING_LENGTH))
    league: Mapped[str] = mapped_column(String(STRING_LENGTH))
    team_id: Mapped[int] = mapped_column(unique=True)

    def __repr__(self) -> str:
        return (
            f"Team(code={self.code!r}, name={self.name!r}, "
            f"league={self.league!r})"
        )


class PythWpc(Base):
    """Table representing Pythagorean Expectation and Win Percentage"""

    __tablename__ = "pyth_wpc"

    pyth_wpc_id: Mapped[str] = mapped_column(primary_key=True)
    team_code: Mapped[str]
    season: Mapped[str]
    league: Mapped[str]
    win_percentage: Mapped[float]
    pythagorean_expectation: Mapped[float]
    last_update: Mapped[datetime.datetime]
