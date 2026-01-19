from pathlib import Path

import os
import json

from .freekick_logging import _logger
from .freekick_config import load_config

CONFIG = load_config(os.getenv("ENV"))
APP_WORKSPACE_DIR = Path(CONFIG["APP_WORKSPACE_DIR"])
SETTING_FILE = APP_WORKSPACE_DIR / "config.json"
DEFAULT_WORKSPACE_SETTINGS = {  # TODO: Store in database instead
    "ESTIMATOR": {
        "EPL": "FreekickDecisionTreeClassifier",
    },
    "DEFAULT_LEAGUE": "EPL",
}

def ensure_workspace() -> None:
    """Ensure workspace directory for application data and files exists."""
    APP_WORKSPACE_DIR.mkdir(exist_ok=True)
    _logger.info(f"App Workspace Dir: {APP_WORKSPACE_DIR}")

    if not SETTING_FILE.exists():
        _logger.info("No config file found, creating a default config..")
        with open(SETTING_FILE, "w") as cfg:
            json.dump(DEFAULT_WORKSPACE_SETTINGS, cfg)
        # TODO: also copy over over persistent models and related data.
        # App should use this directly going forward and not freekick/data
        # This will also make it possible for others to add custom models to
        # use. e.g.: add a model in the ModelCatalog (dir), and app can auto
        # find it or provide plugin to enable model discovery.
    else:
        # update config file but only for configs that are not set in existing
        # file
        data: dict = load_runtime_settings()
        if data != DEFAULT_WORKSPACE_SETTINGS:
            # Do not ovewrite existing settings but ensure we puck
            # up any new config added.
            cp_settings: dict = DEFAULT_WORKSPACE_SETTINGS.copy()
            cp_settings.update(data)
            update_runtime_settings(cp_settings)

def update_runtime_settings(setting_dict: dict) -> None:
    # Load and update config e.g. update and save default learnier
    with open(SETTING_FILE, "w") as sf:
        data = json.load(sf)
        if data != setting_dict:
            data.update(setting_dict)
            json.dump(data, sf)

def load_runtime_settings() -> dict:
    # Load config.
    # Will be useful to pull info to display in frontend.
    with open(SETTING_FILE, "rb") as sf:
        data = json.load(sf)
    return data

def update_estimator_for_league(league, estimator: str) -> None:
    settings = load_runtime_settings()
    # TODO: validate estimator and league are actually valid entries
    settings['ESTIMATOR'][league.name] =  estimator
    update_runtime_settings(settings)

def get_default_estimator(league) -> str:
    return load_runtime_settings['ESTIMATOR'][league]

