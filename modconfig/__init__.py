"""Modconfig to support configuration from modules."""

from importlib import import_module
from inspect import isclass, isbuiltin, ismodule, getmembers
from types import ModuleType
import json
import logging
import os
import typing as t


__version__ = "1.2.0"
__license__ = "MIT"
__all__ = 'Config',


logger: logging.Logger = logging.getLogger('scfg')
identity: t.Callable = lambda v: v  # noqa
types_supported = {int, float, bool, str, bytes, object, list, tuple, dict}


class Config:

    """Basic class to keep a configuration."""

    __slots__ = '__env_prefix', '__storage', '__annotations'

    def __init__(self, *mods: t.Union[str, ModuleType], config_config: t.Dict = None, **options):
        """Initialize the config.

        :param config_config: A dictionary with config's options

        Available options (default):
            - update_from_env (True) update the config from OS environment
            - env_prefix ("") a prefix to read options from OS environment

        """
        opts = config_config or {}

        self.__storage: t.Dict[str, object] = {}
        self.__annotations: t.Dict[str, t.Callable] = {}
        self.__env_prefix: str = opts.get('env_prefix', '')

        if mods:
            self.update_from_modules(*mods)

        self.update(**options)

        if opts.get('update_from_env', True):
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

    def update(self, *mods: t.Union[str, ModuleType], **options):
        """Update the configuration."""
        self.update_from_modules(*mods)
        self.update_from_dict(options, exist_only=False)

    def update_from_dict(
            self, options: t.Mapping, *, exist_only: bool = True, prefix: str = '',
            processor: t.Callable = identity, annotations: t.Dict = None):
        """Update the configuration from given dictionary."""
        annotations = annotations or {}
        prefix = prefix.upper()
        prefix_length = len(prefix)
        for name, value in options.items():
            vtype = annotations.get(name)
            name = name.upper()
            if prefix:
                if not name.startswith(prefix):
                    continue

                name = name[prefix_length:]

            if not name or name.startswith('_'):
                continue

            if exist_only and name not in self.__storage:
                continue

            if name in self.__storage:
                vtype = self.__annotations[name]

            elif exist_only:
                continue

            else:
                if not vtype:
                    vtype = type(value)
                    vtype = identity if vtype not in types_supported else vtype

                self.__annotations[name] = vtype

            try:
                value = processor(value)
                if value is not None:
                    value = vtype(value)
                self.__storage[name] = value
            except (ValueError, TypeError):
                logger.warning(
                    'Ignored invalid configuration value given for %s: %s', name, value)
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
                logger.debug('Ignore invalid configuration module given: %s', mod)
                mod = fallback.pop(0) if fallback else ''

        else:
            return None

        members = getmembers(mod, lambda v: not (isclass(v) or ismodule(v) or isbuiltin(v)))
        self.update_from_dict(
            dict(members), exist_only=exist_only, annotations=t.get_type_hints(mod))
        return mod.__name__

    def update_from_env(self, prefix: str = None):
        """Update the configuration from environment variables."""

        def processor(value):
            try:
                return json.loads(value)
            except ValueError:
                return value

        prefix = (prefix or self.__env_prefix).upper()
        trim = len(prefix)
        options = {n[trim:]: v for n, v in os.environ.items() if n.upper().startswith(prefix)}

        return self.update_from_dict(options, exist_only=True, processor=processor)
