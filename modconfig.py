"""Modconfig to support configuration from modules."""

import json
import logging
import os
from importlib import import_module
from inspect import isclass, isbuiltin, ismodule


__version__ = "0.2.3"
__license__ = "MIT"


logger = logging.getLogger('scfg')


class Config:

    """Basic class to keep a configuration."""

    def __init__(self, *mods, prefix='', update_from_env=True, **options):  # noqa
        self.__prefix__ = prefix
        if mods:
            self.import_mods(*mods)

        self.__dict__.update(options)

        if update_from_env:
            self.update_from_env()

    def import_mods(self, mod, *fallback):
        """Load a module from the given python path or environment."""
        fallback = list(fallback)
        while mod:
            try:
                if isinstance(mod, str):
                    if mod.lower().startswith('env:'):
                        mod = os.environ[mod[4:]]

                    mod = import_module(mod)

                break

            except (ImportError, KeyError):
                logger.error('Invalid configuration module given: %s', mod)
                mod = fallback and fallback.pop(0)
        else:
            return False

        for name in dir(mod):
            if name.startswith('_'):
                continue

            value = getattr(mod, name)
            if isclass(value) or ismodule(value) or isbuiltin(value):
                continue

            self.__dict__[name] = value

    def update_from_env(self):
        """Update the configuration from environment variables."""
        prefix_length = len(self.__prefix__)
        for name in os.environ:
            cfgname = name[prefix_length:]
            if cfgname.startswith('_') or cfgname not in self.__dict__:
                continue

            value = os.environ[name]
            value_type = type(self.__dict__[cfgname])
            try:
                value = json.loads(value)
            except ValueError:
                pass

            try:
                value = value_type(value)
            except (ValueError, TypeError):
                continue

            self.__dict__[cfgname] = value

    def __repr__(self):
        """Representation."""
        return "<Config %r>" % sorted(name for name in self.__dict__ if not name.startswith('_'))
