from sqlalchemy import create_engine

from freekick import DATA_DIR

from .util import DATA_UTIL

# TODO: Load DATABASE_URL from env (load_config.load_config) instead
DB_URL = DATA_DIR / "freekick.db"

DEFAULT_ENGINE = create_engine(
    f"sqlite:///{str(DB_URL)}",
    pool_size=5,  # default in SQLAlchemy
    max_overflow=10,  # default in SQLAlchemy
    pool_timeout=10,  # raise an error faster than default
)

__all__ = ["DATA_UTIL", "DB_URL", "DEFAULT_ENGINE"]
