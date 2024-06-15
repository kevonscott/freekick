"""Data Transfer Objects (DTO) for sending across network.
"""

from dataclasses import dataclass


@dataclass
class MatchDTO:
    home_team: str
    away_team: str
    predicted_winner: str


@dataclass(frozen=True)
class TeamName:
    code: str
    name: str


class SeasonDTO:
    def __init__(self, season: str, teams: list[TeamName]) -> None:
        self.season = season
        self.teams = teams
