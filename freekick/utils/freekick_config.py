import os
from pathlib import Path
from dotenv import load_dotenv
from functools import cache
from .freekick_logging import _logger

@cache
def _set_environ(environment: str) -> None:
    """Set environment variables from .env file"""
    if environment.lower() in {"production", "prod"}:
        load_dotenv("production.env")
        _logger.info("Loaded production.env.")
    elif environment.lower() == "test":
        load_dotenv("testing.env")
        _logger.info("Loaded production.env.")
    else:
        load_dotenv("development.env")
        _logger.info("Loaded production.env.")

def add_env_specific_config(cfg: dict, environment: str) -> dict:
    env = environment.lower()
    db_name: str = cfg["DATABASE_NAME"]
    dev_url = Path(__file__).parent.parent.parent.resolve() / "data" / db_name

    match env:
        case "prod" | "production":
            cfg["DATABASE_URL"] = f"sqlite:///{str(dev_url)}"
        case "dev" | "development":
            cfg["DATABASE_URL"] = f"sqlite:///{str(dev_url)}"
        case "test" | "testing":
            cfg["DATABASE_URL"] = f"sqlite:///{str(dev_url)}"
        case _:
            raise ValueError(f"Invalid env {environment}!")
    return cfg


def load_config(environ: str) -> dict[str, str | bool | None]:
    """Load configs form .env files

    Parameters
    ----------
    environ : str
        Name of .env file. Choice of ['production', 'development']

    Returns
    -------
    dict
        Dictionary with each environment variable
    """
    _set_environ(environ)
    cfg: dict[str, str | bool | None] = {}
    cfg["LOG_LEVEL"] = os.environ.get("LOG_LEVEL")
    cfg["EPL_ESTIMATOR_CLASS"] = os.environ.get("EPL_ESTIMATOR_CLASS")
    WPC_PYTH_STR = os.environ.get("INITIALIZE_WPC_PYTH")
    if WPC_PYTH_STR == "True":
        WPC_PYTH_BOOL = True
    elif WPC_PYTH_STR == "False":
        WPC_PYTH_BOOL = False
    else:
        raise ValueError(
            "Invalid boolean value for INITIALIZE_WPC_PYTH: %s", WPC_PYTH_STR
        )
    cfg["INITIALIZE_WPC_PYTH"] = WPC_PYTH_BOOL
    cfg["DATABASE_NAME"] = os.environ.get("DATABASE_NAME")
    cfg["DATABASE_HOST"] = os.environ.get("DATABASE_HOST")
    cfg["DATABASE_KEY"] = os.environ.get("DATABASE_KEY")
    return add_env_specific_config(cfg, environment=environ)


def coerce_env_dir_name(env_name: str) -> str:
    """Utility function to massage environment directory names/mapping.

    :param env_name: Environment name. E.g. prod, production, dev, etc..
    """
    env_name_lower = env_name.lower()
    match env_name_lower:
        case "production" | "prod":
            env = "prod"
        case "development" | "dev":
            env = "dev"
        case _:
            raise ValueError("Invalid Environment option: %s", env_name)

    return env
