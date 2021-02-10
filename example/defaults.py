from pathlib import Path


ENV = 'production'

SECRET = 'unsecure'

API_KEY = 'something'

APP_DIR: Path = Path(__file__).parent.parent.absolute()

SOME_LIMIT = 42

DATABASE = {
    'host': 'localhost',
    'user': 'guest'
}
