from .util import MatchDTO


def predict_match_day(league: str):
    raise NotImplementedError
    return [
        MatchDTO(
            home_team="Team1", away_team="Team2", predicted_winner="TEAM1"
        ),
        MatchDTO(
            home_team="Team3", away_team="Team4", predicted_winner="TEAM4"
        ),
        MatchDTO(
            home_team="Team6", away_team="Team5", predicted_winner="TEAM6"
        ),
    ]
