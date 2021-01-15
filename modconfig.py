"""Modconfig to support configuration from modules."""

import json
import logging
import os
from importlib import import_module
from inspect import isclass, isbuiltin, ismodule, getmembers


__version__ = "0.4.2"
__license__ = "MIT"
__all__ = 'Config',


logger = logging.getLogger('scfg')
identity = lambda v: v  # noqa
types = {str, int, float, list, tuple, dict, set, bool, bytes}


class Config:

    """Basic class to keep a configuration."""

    def __init__(self, *mods, prefix='', update_from_env=True, **options):  # noqa
        self._prefix = prefix

        if mods:
            self.update_from_modules(*mods)

        self.update(**options)

        if update_from_env:
            self.update_from_env()

    def get(self, name, default=None):
        """Get an item from the config."""
        return self.__dict__.get(name, default)

    def update(self, *mods, **options):
        """Update the configuration."""
        self.update_from_modules(*mods)
        self.update_from_dict(options, exist_only=False)

    def update_from_dict(self, options, prefix='', exist_only=True, processor=identity):
        """Update the configuration from given dictionary."""
        prefix_length = len(prefix)
        for name, value in options.items():
            name = name[prefix_length:]
            if not name or name.startswith('_') or (exist_only and name not in self.__dict__):
                continue

            evalue = self.__dict__.get(name)
            vtype = type(evalue)
            vtype = vtype if vtype in types else identity

            try:
                self.__dict__[name] = vtype(processor(value))
            except (ValueError, TypeError):
                logger.warning('Invalid configuration value given for %s: %s', name, value)
                continue

    def update_from_modules(self, *mods, exist_only=False):
        """Load a module from the given python path or environment."""
        try:
            mod, *fallback = mods
        except ValueError:
            return

        fallback = list(fallback)
        while mod:
            try:
                if isinstance(mod, str):
                    if mod.lower().startswith('env:'):
                        mod = os.environ[mod[4:]]

                    mod = import_module(mod)

                break

            except (ImportError, KeyError):
                logger.warning('Invalid configuration module given: %s', mod)
                mod = fallback and fallback.pop(0)
        else:
            return

        members = getmembers(mod, lambda v: not (isclass(v) or ismodule(v) or isbuiltin(v)))
        self.update_from_dict(dict(members), exist_only=exist_only)

    def update_from_env(self):
        """Update the configuration from environment variables."""

        def processor(value):
            try:
                return json.loads(value)
            except ValueError:
                return value

        self.update_from_dict(
            dict(os.environ), prefix=self._prefix, exist_only=True, processor=processor)

    def __repr__(self):
        """Representation."""
        return "<Config %r>" % sorted(name for name in self.__dict__ if not name.startswith('_'))
