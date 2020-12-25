import pytest


def test_base(Config):
    cfg = Config('unknown')
    assert cfg
    with pytest.raises(AttributeError):
        cfg.UNKNOWN

    cfg = Config(OPTION=42)
    assert cfg
    assert cfg.OPTION == 42

    cfg.update(OPTION=43)
    assert cfg.OPTION == 43

    cfg.update_from_modules()


def test_fallback(Config):
    """If the first given module is not available then next would be used."""
    cfg = Config('example.unknown', 'example.tests', 'example.production')
    assert cfg.ENV == 'tests'


def test_import_modules(Config):
    from example import tests

    # Config accepts modules themself
    cfg = Config(tests)
    assert cfg
    assert cfg.SECRET == 'unsecure'

    # Config accepts modules import path
    cfg = Config('example.tests', API_KEY='redefined')
    assert cfg
    assert cfg.SECRET == 'unsecure'
    assert cfg.API_KEY == 'redefined'
    assert cfg.ENV == 'tests'
    assert cfg.APP_DIR


def test_env(Config, monkeypatch):
    # Config accepts modules path from ENV variables
    monkeypatch.setenv('MODCONFIG', 'example.production')
    cfg = Config('ENV:MODCONFIG')
    assert cfg.DATABASE['host'] == 'db.com'

    # Any var from config could be redefined in ENV
    monkeypatch.setenv('API_KEY', 'prod_key')
    monkeypatch.setenv('DATABASE', '[1,2,3]')
    monkeypatch.setenv('SOME_LIMIT', '100')
    cfg = Config('example.production')
    assert cfg.API_KEY == 'prod_key'
    assert cfg.SOME_LIMIT == 100
    # Invalid types would be ignored
    assert cfg.DATABASE == {'host': 'db.com', 'user': 'guest'}

    # Correct types would be parsed
    monkeypatch.setenv('DATABASE', '{"host": "new.com", "user": "admin"}')
    cfg = Config('example.production')
    assert cfg.DATABASE == {'host': 'new.com', 'user': 'admin'}

    monkeypatch.setenv('APP_SECRET', 'value_from_env_with_prefix')
    cfg = Config('example.production', _prefix='APP_')
    assert cfg.SECRET == 'value_from_env_with_prefix'


@pytest.fixture
def Config():
    from modconfig import Config as klass

    return klass
