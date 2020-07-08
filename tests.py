import pytest


@pytest.fixture
def Config():
    from modconfig import Config as klass

    return klass


def test_base(Config):
    assert Config

    cfg = Config('unknown')
    assert cfg
    with pytest.raises(AttributeError):
        cfg.UNKNOWN

    cfg = Config('', OPTION=42)
    assert cfg
    assert cfg.OPTION == 42


def test_import_modules(Config):
    from example import tests

    cfg = Config(tests)
    assert cfg
    assert cfg.SECRET == 'unsecure'

    cfg = Config('example.tests', API_KEY='redefined')
    assert cfg
    assert cfg.SECRET == 'unsecure'
    assert cfg.API_KEY == 'redefined'
    assert cfg.ENV == 'tests'
    assert cfg.APP_DIR


def test_env(Config, monkeypatch):
    cfg = Config('example.production')
    assert cfg.DATABASE['host'] == 'db.com'

    monkeypatch.setenv('API_KEY', 'prod_key')
    monkeypatch.setenv('DATABASE', '[1,2,3]')
    monkeypatch.setenv('SOME_LIMIT', '100')
    cfg = Config('example.production')
    assert cfg.API_KEY == 'prod_key'
    assert cfg.SOME_LIMIT == 100
    assert cfg.DATABASE == {'host': 'db.com', 'user': 'guest'}

    monkeypatch.setenv('DATABASE', '{"host": "new.com", "user": "admin"}')
    cfg = Config('example.production')
    assert cfg.DATABASE == {'host': 'new.com', 'user': 'admin'}
