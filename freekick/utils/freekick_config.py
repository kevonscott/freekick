import os
from dotenv import load_dotenv


def _set_environ(environment):
    """Set environment variables from .env file"""
    if environment == "production":
        load_dotenv("production.env")
    else:
        load_dotenv("development.env")


def load_config(environ):
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
    cfg = {}
    cfg["DATABASE_NAME"] = os.environ.get("DATABASE_NAME")
    cfg["DATABASE_HOST"] = os.environ.get("DATABASE_HOST")
    cfg["DATABASE_KEY"] = os.environ.get("DATABASE_KEY")

    return cfg
