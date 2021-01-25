"""Modconfig to support configuration from modules."""

import json
import logging
import os
import typing as t
from importlib import import_module
from inspect import isclass, isbuiltin, ismodule, getmembers
from types import ModuleType


__version__ = "0.9.1"
__license__ = "MIT"
__all__ = 'Config',


logger: logging.Logger = logging.getLogger('scfg')
identity: t.Callable = lambda v: v  # noqa
types: t.Set = {str, int, float, list, tuple, dict, set, bool, bytes}


class Config:
    """Basic class to keep a configuration."""

    __slots__ = 'prefix', 'ignore_case', 'storage'

    def __init__(
            self, *mods: t.Union[str, ModuleType], prefix: str = '', update_from_env: bool = True,
            ignore_case: bool = False, **options):  # noqa
        self.storage: t.Dict[str, object] = {}
        self.prefix: str = prefix
        self.ignore_case: bool = ignore_case

        if mods:
            self.update_from_modules(*mods)

        self.update(**options)

        if update_from_env:
            self.update_from_env()

    def __repr__(self) -> str:
        """Representation."""
        return "<Config %r>" % sorted(name for name in self.storage if not name.startswith('_'))

    def __iter__(self) -> t.Iterator:
        """Iterate through self."""
        return ((k, v) for k, v in self.storage.items() if not k.startswith('_'))

    def __getattr__(self, name: str):
        """Proxy attributes to self storage."""
        try:
            return self.storage[name]
        except KeyError:
            raise AttributeError(f'Invalid option: {name}')

    def get(self, name: str, default: t.Any = None) -> t.Any:
        """Get an item from the config."""
        return self.storage.get(name, default)

    def update(self, *mods: t.Union[str, ModuleType], **options):
        """Update the configuration."""
        self.update_from_modules(*mods)
        self.update_from_dict(options, exist_only=False)

    def update_from_dict(
            self, options: t.Mapping, /, prefix: str = '', exist_only: bool = True,
            ignore_case: bool = None, processor: t.Callable = identity):
        """Update the configuration from given dictionary."""
        if ignore_case is None:
            ignore_case = self.ignore_case

        prefix_length = len(prefix)
        for name, value in options.items():
            name = name[prefix_length:]
            if not name or name.startswith('_'):
                continue

            key = name
            if ignore_case:
                lname = name.lower()
                for key in self.storage:
                    if key.lower() == lname:
                        break
                else:
                    key = name

            if exist_only and key not in self.storage:
                continue

            evalue = self.storage.get(key)
            vtype = type(evalue)
            type_processor = vtype if vtype in types else identity

            try:
                self.storage[key] = type_processor(processor(value))  # type: ignore
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
                if fallback:
                    mod = fallback.pop(0)

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
            dict(os.environ), prefix=self.prefix, exist_only=True, processor=processor)
