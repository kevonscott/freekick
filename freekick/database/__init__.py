from pathlib import Path

from sqlalchemy import create_engine

# TODO: Load DATABASE_URL from env (load_config.load_config) instead
DB_URL = Path(__file__).parent.parent.parent / "data" / "freekick.db"

DEFAULT_ENGINE = create_engine(f"sqlite:///{str(DB_URL)}")
