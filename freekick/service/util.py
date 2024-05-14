class MatchDTO:  # Move to services
    def __init__(self, home_team, away_team, predicted_winner) -> None:
        self.home_team = home_team
        self.away_team = away_team
        self.predicted_winner = predicted_winner
