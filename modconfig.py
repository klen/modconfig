import json
import logging
import os
from importlib import import_module
from inspect import isclass, isbuiltin, ismodule


__version__ = "0.1.1"
__license__ = "MIT"


logger = logging.getLogger('scfg')


class Config:

    def __init__(self, mod, **scope):  # noqa
        if mod:
            try:
                if isinstance(mod, str):
                    mod = import_module(mod)

                for name in dir(mod):
                    if name.startswith('_'):
                        continue

                    value = getattr(mod, name)
                    if isclass(value) or ismodule(value) or isbuiltin(value):
                        continue

                    scope.setdefault(name, value)

            except ImportError:
                logger.error('Invalid configuration module given: %s', mod)

        self.__dict__.update(scope)

        for name in os.environ:
            if not hasattr(self, name):
                continue

            value = os.environ[name]
            value_type = type(getattr(self, name))
            try:
                value = json.loads(value)
            except ValueError:
                pass

            try:
                value = value_type(value)
            except (ValueError, TypeError):
                continue

            setattr(self, name, value)

    def __repr__(self):
        return "<Config %r>" % sorted(name for name in self.__dict__ if not name.startswith('_'))
