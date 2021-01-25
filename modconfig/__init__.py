"""Modconfig to support configuration from modules."""

import json
import logging
import os
import typing as t
from importlib import import_module
from inspect import isclass, isbuiltin, ismodule, getmembers
from types import ModuleType


__version__ = "0.10.2"
__license__ = "MIT"
__all__ = 'Config',


logger: logging.Logger = logging.getLogger('scfg')
identity: t.Callable = lambda v: v  # noqa
types: t.Set = {str, int, float, list, tuple, dict, set, bool, bytes}


class Config:
    """Basic class to keep a configuration."""

    __slots__ = '__prefix', '__storage'

    def __init__(
            self, *mods: t.Union[str, ModuleType], prefix: str = '',
            update_from_env: bool = True, **options):  # noqa
        self.__storage: t.Dict[str, object] = {}
        self.__prefix: str = prefix

        if mods:
            self.update_from_modules(*mods)

        self.update(**options)

        if update_from_env:
            self.update_from_env()

    def __repr__(self) -> str:
        """Representation."""
        return "<Config %r>" % self.__storage

    def __iter__(self) -> t.Iterator:
        """Iterate through self."""
        return iter(self.__storage.items())

    def __getattr__(self, name: str) -> t.Any:
        """Proxy attributes to self storage."""
        try:
            return self.__storage[name.upper()]
        except KeyError:
            raise AttributeError(f'Invalid option: {name}')

    def __getitem__(self, name: str) -> t.Any:
        """Proxy attributes to self storage."""
        return self.__storage[name.upper()]

    def get(self, name: str, default: object = None) -> t.Any:
        """Get an item from the config."""
        return self.__storage.get(name.upper(), default)

    @property
    def prefix(self) -> str:
        """Return self prefix."""
        return self.__prefix

    def update(self, *mods: t.Union[str, ModuleType], **options):
        """Update the configuration."""
        self.update_from_modules(*mods)
        self.update_from_dict(options, exist_only=False)

    def update_from_dict(
            self, options: t.Mapping, /, prefix: str = '', exist_only: bool = True,
            processor: t.Callable = identity):
        """Update the configuration from given dictionary."""
        prefix_length = len(prefix)
        for name, value in options.items():
            name = name[prefix_length:]
            if not name or name.startswith('_'):
                continue

            name = name.upper()
            type_processor = identity
            try:
                evalue = self.__storage[name]
                vtype: t.Callable = type(evalue)
                type_processor = vtype if vtype in types else type_processor
            except KeyError:
                if exist_only:
                    continue

            try:
                self.__storage[name] = type_processor(processor(value))  # type: ignore
            except (ValueError, TypeError):
                logger.warning('Invalid configuration value given for %s: %s', name, value)
                continue

    def update_from_modules(
            self, *mods: t.Union[str, ModuleType], exist_only: bool = False) -> t.Optional[str]:
        """Load a module from the given python path or environment."""
        try:
            mod, *fallback = mods
        except ValueError:
            return None

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
                mod = fallback.pop(0) if fallback else ''

        else:
            return None

        members = getmembers(mod, lambda v: not (isclass(v) or ismodule(v) or isbuiltin(v)))
        self.update_from_dict(dict(members), exist_only=exist_only)
        return mod.__name__

    def update_from_env(self):
        """Update the configuration from environment variables."""

        def processor(value):
            try:
                return json.loads(value)
            except ValueError:
                return value

        self.update_from_dict(
            dict(os.environ), prefix=self.__prefix, exist_only=True, processor=processor)
