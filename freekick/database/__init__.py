from pathlib import Path

from sqlalchemy import create_engine

from freekick import DATA_DIR

# TODO: Load DATABASE_URL from env (load_config.load_config) instead
DB_URL = DATA_DIR / "freekick.db"

DEFAULT_ENGINE = create_engine(f"sqlite:///{str(DB_URL)}")
