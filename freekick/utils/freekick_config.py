import os
from dotenv import load_dotenv


def _set_environ(environment):
    if environment == "production":
        load_dotenv("production.env")
    else:
        load_dotenv("development.env")


def load_config(environ):
    _set_environ(environ)
    cfg = {}
    cfg["BUNDESLIGA_CSV"] = os.environ.get("BUNDESLIGA_CSV")
    cfg["EPL_CSV"] = os.environ.get("EPL_CSV")
    cfg["DATABASE_NAME"] = os.environ.get("DATABASE_NAME")
    cfg["DATABASE_HOST"] = os.environ.get("DATABASE_HOST")
    cfg["DATABASE_KEY"] = os.environ.get("DATABASE_KEY")

    return cfg
