import datetime as dt
from pathlib import Path
from typing import Dict

ENV = "production"

SECRET = "unsecure"

API_KEY = "something"

APP_DIR: Path = Path(__file__).parent.parent.absolute()

API_TOKEN_EXPIRE = dt.timedelta(days=60)

SOME_LIMIT = 42

DATABASE: Dict[str, str] = {"host": "localhost", "user": "guest"}
