import json
import logging
import os
from importlib import import_module
from inspect import isclass, isbuiltin, ismodule


__version__ = "0.1.2"
__license__ = "MIT"


logger = logging.getLogger('scfg')


class Config:

    def __init__(self, *mods, **scope):  # noqa
        if mods:
            mod = import_mod(*mods)
            if mod:
                for name in dir(mod):
                    if name.startswith('_'):
                        continue

                    value = getattr(mod, name)
                    if isclass(value) or ismodule(value) or isbuiltin(value):
                        continue

                    scope.setdefault(name, value)

        scope = update_from_env(scope)
        self.__dict__.update(scope)

    def __repr__(self):
        return "<Config %r>" % sorted(name for name in self.__dict__ if not name.startswith('_'))


def import_mod(mod, *fallback):
    """Load a module from python import path or environment."""
    fallback = list(fallback)
    while mod:
        try:
            if isinstance(mod, str):
                if mod.startswith('ENV:'):
                    mod = os.environ[mod[4:]]

                mod = import_module(mod)

            break

        except (ImportError, KeyError):
            logger.error('Invalid configuration module given: %s', mod)
            mod = fallback and fallback.pop(0)

    return mod


def update_from_env(scope):
    """Update the fiven configuration scope from OS Environment."""
    for name in os.environ:
        if name not in scope:
            continue

        value = os.environ[name]
        value_type = type(scope[name])
        try:
            value = json.loads(value)
        except ValueError:
            pass

        try:
            value = value_type(value)
        except (ValueError, TypeError):
            continue

        scope[name] = value

    return scope
