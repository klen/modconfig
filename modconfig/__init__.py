"""Modconfig to support configuration from modules."""

from importlib import import_module
from inspect import isclass, isbuiltin, ismodule, getmembers
from types import ModuleType
import json
import logging
import os
import typing as t


__version__ = "0.15.0"
__license__ = "MIT"
__all__ = 'Config',


logger: logging.Logger = logging.getLogger('scfg')
identity: t.Callable = lambda v: v  # noqa


class Config:
    """Basic class to keep a configuration."""

    __slots__ = '__prefix', '__storage', '__annotations'

    def __init__(
            self, *mods: t.Union[str, ModuleType], config_prefix: str = '',
            config_update_from_env: bool = True, **options):  # noqa
        self.__storage: t.Dict[str, object] = {}
        self.__annotations: t.Dict[str, t.Callable] = {}
        self.__prefix: str = config_prefix

        if mods:
            self.update_from_modules(*mods)

        self.update(**options)

        if config_update_from_env:
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
            self, options: t.Mapping, *, config_prefix: str = '', exist_only: bool = True,
            processor: t.Callable = identity, annotations: t.Dict = None):
        """Update the configuration from given dictionary."""
        prefix_length = len(config_prefix)
        annotations = annotations or {}
        for name, value in options.items():
            vtype = annotations.get(name)
            name = name[prefix_length:]
            if not name or name.startswith('_'):
                continue

            name = name.upper()
            if exist_only and name not in self.__storage:
                continue

            if name in self.__storage:
                vtype = self.__annotations[name]

            elif exist_only:
                continue

            else:
                if not vtype:
                    vtype = vtype or type(value) if value is not None and not callable(value) else identity  # noqa

                self.__annotations[name] = vtype

            try:
                value = processor(value)
                if value is not None:
                    value = vtype(value)
                self.__storage[name] = value
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
                logger.debug('Invalid configuration module given: %s', mod)
                mod = fallback.pop(0) if fallback else ''

        else:
            return None

        members = getmembers(mod, lambda v: not (isclass(v) or ismodule(v) or isbuiltin(v)))
        self.update_from_dict(
            dict(members), exist_only=exist_only, annotations=t.get_type_hints(mod))
        return mod.__name__

    def update_from_env(self):
        """Update the configuration from environment variables."""

        def processor(value):
            try:
                return json.loads(value)
            except ValueError:
                return value

        self.update_from_dict(
            dict(os.environ), config_prefix=self.__prefix, exist_only=True, processor=processor)
