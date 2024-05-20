import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

STRING_LENGTH = 50


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    home_team: Mapped[int] = mapped_column(ForeignKey("team.id"))
    away_team: Mapped[int] = mapped_column(ForeignKey("team.id"))
    home_goal: Mapped[int]
    away_goal: Mapped[int]
    season: Mapped[Optional[str]]
    league: Mapped[str]
    date: Mapped[datetime.date]
    time: Mapped[Optional[str]]
    attendance: Mapped[Optional[float]]

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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column(String(STRING_LENGTH))
    league: Mapped[str] = mapped_column(String(STRING_LENGTH))

    def __repr__(self) -> str:
        return (
            f"Team(code={self.code!r}, name={self.name!r}, " f"league={self.league!r})"
        )
