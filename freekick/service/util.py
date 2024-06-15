"""Data Transfer Objects (DTO) for sending across network.
"""

from dataclasses import dataclass

from freekick.datastore.util import TeamName


@dataclass
class MatchDTO:
    home_team: str
    away_team: str
    predicted_winner: str


class SeasonDTO:
    def __init__(self, season: str, teams: list[TeamName]) -> None:
        self.season = season
        self.teams = teams
