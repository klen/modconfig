import pytest


def test_base():
    from modconfig import Config

    cfg = Config('unknown')
    assert cfg
    with pytest.raises(AttributeError):
        cfg.UNKNOWN

    cfg = Config(OPTION=42)
    assert cfg
    assert cfg.OPTION == 42
    assert cfg.get('OPTION') == 42
    assert cfg.get('UNKNOWN', True)

    cfg.update(OPTION=43)
    assert cfg.OPTION == 43

    cfg.update_from_modules()

    test = list(cfg)
    assert test == [('OPTION', 43)]


def test_update_from_dict():
    from modconfig import Config

    cfg = Config(ignore_case=True, var1=1, VAR2=2)
    cfg.update_from_dict({'CFG_VAR1': 11, 'CFG_VAR3': 33}, prefix='CFG_')
    assert cfg.var1 == 11
    assert cfg.VAR2 == 2
    with pytest.raises(AttributeError):
        assert cfg.var3


def test_import_modules():
    from modconfig import Config
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

    #  If the first given module is not available then next would be used.
    cfg = Config('example.unknown', 'example.tests', 'example.production')
    assert cfg.ENV == 'tests'


def test_env(monkeypatch):
    from modconfig import Config

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
    cfg = Config('example.production', prefix='APP_')
    assert cfg.SECRET == 'value_from_env_with_prefix'


# pylama:ignore=D
