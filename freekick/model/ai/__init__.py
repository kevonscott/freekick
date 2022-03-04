"""Model for all Artificial Intelligence and Machine Learning Operations."""
from functools import partial, lru_cache
import os
import pickle
import logging
import pkg_resources

_LEAGUES = ["epl", "bundesliga"]

logging.basicConfig()
_logger = logging.getLogger("Freekick-AI")
_logger.setLevel(logging.INFO)


def _load_model(model_name: str):
    """Load serial models"""
    model_path = pkg_resources.resource_filename(
        __name__, os.path.join("serialized_models", model_name)
    )
    with open(model_path, "rb") as plk_file:
        model = pickle.load(plk_file)
        _logger.info(f"     - {model_name}")
    return model


@lru_cache()
def load_models():
    _logger.info(" Loading serial models...")
    return {league: _load_model(model_name=f"{league}.pkl") for league in _LEAGUES}


serial_models = partial(load_models)
# _MODELS = list(serial_models.keys())
# _LEAGUES = _MODELS

####### Team names and short codes #########################
# reference for the names: https://www.sporcle.com/games/easterbunny/football-club--by-abbreviations-/results
soccer_teams = {
    "epl": {
        "Arsenal": "ARS",
        "Aston Villa": "AVL",
        "Barnsley": "BAR",
        "Blackburn": "BLA",
        "Blackpool": "BLP",  # Manually  renamed due to conflick with BLA
        "Birmingham": "BIR",
        "Bolton": "BOL",
        "Bournemouth": "BOU",
        "Bradford": "BRA",
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
        "Liverpool": "LIV",
        "Man City": "MCI",
        "Manchester City": "MCI",
        "Manchester United": "MUN",
        "Man United": "MUN",
        "Middlesbrough": "MID",
        "Newcastle United": "NEW",
        "Newcastle": "NEW",
        "Norwich": "NOR",
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

current_season_teams = {"epl": [], "bundesliga": []}
