import pytest


def test_base():
    from modconfig import Config

    cfg = Config('unknown', config_config=dict(env_prefix='CONFIG'))
    assert cfg
    assert cfg._Config__env_prefix == 'CONFIG'
    with pytest.raises(AttributeError):
        cfg.UNKNOWN

    cfg = Config(OPTION=42)
    assert cfg
    assert cfg.OPTION == 42
    assert cfg.get('OPTION') == 42
    assert cfg.get('UNKNOWN', True)

    cfg.update(OPTION=43)
    assert cfg.OPTION == 43

    test = cfg.update_from_modules()
    assert not test

    test = list(cfg)
    assert test == [('OPTION', 43)]

    cfg.update(fn=lambda: 42)
    assert cfg.FN() == 42


def test_update_from_dict():
    from modconfig import Config

    cfg = Config(ignore_case=True, var1=1, VAR2=2)
    cfg.update_from_dict({'CFG_VAR1': 11, 'CFG_VAR3': 33}, prefix='CFG_')
    assert cfg.var1 == 11
    assert cfg.VAR2 == 2
    with pytest.raises(AttributeError):
        assert cfg.var3

    cfg = Config(VAR=42)
    cfg.update_from_dict({'CFG_VAR': 11, 'VAR': 22}, prefix='CFG_')
    assert cfg.var == 11


def test_import_modules():
    from modconfig import Config
    from example import tests

    # Config accepts modules themself
    cfg = Config(tests)
    assert cfg
    assert cfg.SECRET == 'unsecure'
    assert cfg.LIMIT is None
    assert cfg.API_TOKEN_EXPIRE

    # Config accepts modules import path
    cfg = Config('example.tests', API_KEY='redefined')
    assert cfg
    assert cfg.API_KEY == 'redefined'
    assert cfg.APP_DIR
    assert cfg.ENV == 'tests'
    assert cfg.LIMIT is None
    assert cfg.SECRET == 'unsecure'

    cfg.update_from_dict({'limit': '0.22'})
    assert cfg.LIMIT == 0.22

    mod = cfg.update_from_modules('example.unknown')
    assert not mod

    #  If the first given module is not available then next would be used.
    mod = cfg.update_from_modules('example.unknown', 'example.tests', 'example.production')
    assert mod == 'example.tests'
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
    monkeypatch.setenv('DEMOENV', 'ignore_me')
    cfg = Config('example.production', config_config=dict(env_prefix='APP_'))
    assert cfg.SECRET == 'value_from_env_with_prefix'
    assert cfg.ENV == 'production'


# pylama:ignore=D
