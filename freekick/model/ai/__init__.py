"""Model for all Artificial Intelligence and Machine Learning Operations."""
import os
import pickle
import pkg_resources
from typing import Union
from functools import partial, lru_cache

from freekick import _logger

_LEAGUES = ["epl"]
# _SEASON = "2021-2022"


def _load_model(model_name: str):
    """Load serial models"""
    model_path = pkg_resources.resource_filename(
        __name__, os.path.join("serialized_models", model_name)
    )
    with open(model_path, "rb") as plk_file:
        model = pickle.load(plk_file)
        _logger.debug(f"     - {model_name}")
    return model


@lru_cache()
def load_models():
    _logger.debug(" Loading serial models...")
    return {league: _load_model(model_name=f"{league}.pkl") for league in _LEAGUES}


serial_models = partial(load_models)
# _MODELS = list(serial_models.keys())
# _LEAGUES = _MODELS


def get_team_code(
    league: str,
    team_name: str,
    code_type: str = "str",
    team_code: Union[str, None] = None,
) -> str:
    """Looks up a team's code name given its full name.

    Parameters
    ----------
    league : str
        The teams 3 letter code
    team_name : str
        Full name of the team

    code_type: str
        Type of code to get. Choices are ['str', 'int']. Default is 'str'.
        Note that if you
    team_code:
        if team code is provided, use team_code instead of team name ogt int
        code type
    Returns
    -------
    str
        Three letter code representing the team

    Raises
    ------
    ValueError
        Value error if invalid team of league name is provided
    """
    if code_type == "str":
        try:
            return soccer_teams[league][team_name]
        except KeyError:
            raise ValueError(f"Invalid league ({league}) or team_name ({team_name})")
    elif code_type == "int":
        team_code_str = team_code or soccer_teams[league][team_name]
        return soccer_teams_int[league][team_code_str]
    else:
        raise ValueError(f"Invalid code_type ({code_type})")


####### Team names and short codes #########################
# reference for the names: https://www.sporcle.com/games/easterbunny/football-club--by-abbreviations-/results
soccer_teams = {
    "epl": {
        "Arsenal": "ARS",
        "ARS": "ARS",
        "Aston Villa": "AVL",
        "Barnsley": "BAR",
        "Blackburn": "BLA",
        "Blackpool": "BLP",  # Manually  renamed due to conflict with BLA
        "Birmingham": "BIR",
        "Bolton": "BOL",
        "Bournemouth": "BOU",
        "Bradford": "BRA",
        "Brentford": "BRE",
        "Brighton": "BHA",
        "Brighton and Hove Albion": "BHA",
        "Burnley": "BUR",
        "Cardiff": "CAR",
        "Charlton": "CHA",
        "Chelsea": "CHE",
        "Coventry": "COV",
        "Crystal Palace": "CRY",
        "Derby": "DER",
        "Everton": "EVE",
        "Fulham": "FUL",
        "Huddersfield": "HUD",
        "Hull": "HUL",
        "Hull City": "HUL",
        "Ipswich": "IPS",
        "Leeds": "LEE",
        "Leeds United": "LEE",
        "Leicester City": "LEI",
        "Leicester": "LEI",
        "LEI": "LEI",
        "Liverpool": "LIV",
        "Man City": "MCI",
        "Manchester City": "MCI",
        "Manchester United": "MUN",
        "Man United": "MUN",
        "MUN": "MUN",
        "Middlesbrough": "MID",
        "Newcastle United": "NEW",
        "Newcastle": "NEW",
        "Norwich": "NOR",
        "Norwich City": "NOR",
        "Nottingham Forest": "FOR",
        "Nott'm Forest": "FOR",
        "Oldham": "OLD",
        "Portsmouth": "POR",
        "QPR": "QPR",
        "Queens Park Rangers": "QPR",
        "Reading": "REA",
        "Southampton": "SOU",
        "Sheffield United": "SHU",
        "Sheffield Weds": "SHW",
        "Sheffield Wednesday": "SHW",
        "Stoke": "STO",
        "STO": "STO",
        "Stoke City": "STO",
        "Sunderland": "SUN",
        "Swansea": "SWA",
        "Swindon": "SWI",
        "Tottenham": "TOT",
        "Tottenham Hotspur": "TOT",
        "Watford": "WAT",
        "West Bromwich Albion": "WBA",
        "West Brom": "WBA",
        "West Ham United": "WHU",
        "West Ham": "WHU",
        "Wigan": "WIG",
        "Wimbledon": "WIM",
        "Wolves": "WOL",
        "Wolverhampton Wanderers": "WOL",
        "Wolverhampton": "WOL",
    },
    "bundesliga": {
        "Arminia Bielefeld": "BIE",
        "Bayer Leverkusen": "B04",
        "Borussia Dortmund": "DOR",
        "Borussia Monchengladbach": "BMG",
        "Eintracht Frankfurt": "SGE",
        "Bayern Munich": "BAY",
        "Bayern Munchen": "BAY",
        "Freiburg": "SCF",
        "Mainz": "MAI",
        "Mainz 05": "MAI",
        "Stuttgart": "STU",
        "VfB Stuttgart": "STU",
        "Bochum": "BOC",
        "VfL Bochum": "BOC",
        "Wolfsburg": "WOB",
        "VfL Wolfsburg": "WOB",
        "Cologne": "CGN",
        "Augsburg": "AUG",
        "FC Augsburg": "AUG",
        "Greuther Fuerth": "GRF",
        "Hertha Berlin": "BCS",
        "Hoffenheim": "TSG",
        "RB Leipzig": "RBL",
        "Union Berlin": "UNB",
    },
}

soccer_teams_int = {
    "epl": {
        "ARS": 1,
        "AVL": 2,
        "BAR": 3,
        "BLA": 4,
        "BLP": 5,  # Manually  renamed due to conflict with BLA
        "BIR": 6,
        "BOL": 7,
        "BOU": 8,
        "BRA": 9,
        "BRE": 10,
        "BHA": 11,
        "BUR": 12,
        "CAR": 13,
        "CHA": 14,
        "CHE": 15,
        "COV": 16,
        "CRY": 17,
        "DER": 18,
        "EVE": 19,
        "FUL": 20,
        "HUD": 21,
        "HUL": 22,
        "IPS": 23,
        "LEE": 24,
        "LEI": 25,
        "LIV": 26,
        "MCI": 27,
        "MUN": 28,
        "MID": 29,
        "NEW": 30,
        "NOR": 31,
        "FOR": 32,
        "OLD": 33,
        "POR": 34,
        "QPR": 35,
        "REA": 36,
        "SOU": 37,
        "SHU": 38,
        "SHW": 39,
        "STO": 40,
        "SUN": 41,
        "SWA": 42,
        "SWI": 43,
        "TOT": 44,
        "WAT": 45,
        "WBA": 46,
        "WHU": 47,
        "WIG": 48,
        "WIM": 49,
        "WOL": 50,
    },
    # "bundesliga": {
    #     "Arminia Bielefeld": "BIE",
    #     "Bayer Leverkusen": "B04",
    #     "Borussia Dortmund": "DOR",
    #     "Borussia Monchengladbach": "BMG",
    #     "Eintracht Frankfurt": "SGE",
    #     "Bayern Munich": "BAY",
    #     "Bayern Munchen": "BAY",
    #     "Freiburg": "SCF",
    #     "Mainz": "MAI",
    #     "Mainz 05": "MAI",
    #     "Stuttgart": "STU",
    #     "VfB Stuttgart": "STU",
    #     "Bochum": "BOC",
    #     "VfL Bochum": "BOC",
    #     "Wolfsburg": "WOB",
    #     "VfL Wolfsburg": "WOB",
    #     "Cologne": "CGN",
    #     "Augsburg": "AUG",
    #     "FC Augsburg": "AUG",
    #     "Greuther Fuerth": "GRF",
    #     "Hertha Berlin": "BCS",
    #     "Hoffenheim": "TSG",
    #     "RB Leipzig": "RBL",
    #     "Union Berlin": "UNB",
    # },
}

current_season_teams = {"epl": [], "bundesliga": []}
