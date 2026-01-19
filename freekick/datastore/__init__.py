import os
from typing import Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from freekick.utils import load_config
from .repository import SQLAlchemyRepository
from .util import DATA_UTIL, League


ENV: str | None = os.environ.get("ENV", None)
CFG: dict = load_config(environ=ENV)
DB_URL: str = CFG["DATABASE_URL"]

DEFAULT_SESSION: Optional[Session] = None

DEFAULT_ENGINE: Engine|None = None


# TODO: Think about making this session a callable so we only create sessions
# when needed instead of always having a session connected
# Sessions and repos should only be instantiated in DB mode.
def get_or_create_session() -> Session:
    """Get existing or create a new Database Session."""
    global DEFAULT_SESSION
    if DEFAULT_SESSION:
        return DEFAULT_SESSION
    else:
        DEFAULT_SESSION = Session(get_or_create_engine())
    return DEFAULT_SESSION

def get_or_create_engine() -> Engine:
    """Get existing or create a new Database Session."""
    global DEFAULT_ENGINE
    if DEFAULT_ENGINE:
        return DEFAULT_ENGINE
    else:
        DEFAULT_ENGINE = create_engine(
            DB_URL,  # f"sqlite:///{str(DB_URL)}",
            pool_size=5,  # default in SQLAlchemy
            max_overflow=10,  # default in SQLAlchemy
            pool_timeout=10,  # raise an error faster than default
        )
    return DEFAULT_ENGINE

DEFAULT_REPOSITORY = SQLAlchemyRepository(get_or_create_session())

__all__ = [
    "DATA_UTIL",
    "get_or_create_engine",
    "get_or_create_session",
    "DEFAULT_REPOSITORY",
    "League"
]
