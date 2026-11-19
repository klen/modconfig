# modconfig

[![Tests](https://github.com/klen/modconfig/workflows/tests/badge.svg)](https://github.com/klen/modconfig/actions)
[![PyPI](https://img.shields.io/pypi/v/modconfig)](https://pypi.org/project/modconfig/)
[![Python](https://img.shields.io/pypi/pyversions/modconfig)](https://pypi.org/project/modconfig/)
[![License](https://img.shields.io/pypi/l/modconfig)](https://opensource.org/licenses/MIT)

Simple hierarchic configuration manager for apps.

## Motivation

Applications (especially web services) often require certain configuration
options to depend on the environment an application runs in (development,
testing, production, etc.). For instance, a database address config option may
default to a local database server during development, a mock database server
during testing, and yet another database server during production. It may also
need to be customizable via an environment variable. `modconfig` approaches
scenarios like this, and allows you to specify default configuration options
for various environments and optionally override them by custom environment
variables.

`modconfig` uses Python modules to keep the configuration options. You are not
locked by format (json, yaml, ini) restrictions and are able to use any Python
statements/modules to tune your configuration as a pro. It keeps the
flexibility and makes your configuration very declarative without any magic.

## Requirements

- Python >= 3.11

## Installation

```bash
pip install modconfig
```

## Usage

For example you have the structure in your app:

```text
|- myapp/
|  |- __init__.py
|  |- config/
|  |  |- __init__.py
|  |  |- defaults.py
|  |  |- production.py
|  |  |- stage.py
|  |  |- tests.py
|  | ...
```

See the [example](https://github.com/klen/modconfig/tree/develop/example) as a
simple reference.

Initialize the config in your app and use it anywhere:

```python
from modconfig import Config

cfg = Config(
    # instead an import path it could be the module itself
    "myapp.config.production",
    # Override any options
    ANY_OPTION1="VALUE",
    ANY_OPTION2="VALUE",
)

assert cfg.DATABASE
assert cfg.ANY_OPTION1
```

Option names are case-insensitive: `cfg.DATABASE`, `cfg.database` and
`cfg["database"]` return the same value. The type of an option comes from the
first value it receives, or from a bare type hint in the config module
(`LIMIT: int = 5`); anything set later is converted to that type, and a value
that cannot be converted is logged and ignored.

### Fallbacks

With several modules, `modconfig` uses the first one it can import:

```python
from modconfig import Config

cfg = Config("myapp.config.local", "myapp.config.production", ANY_OPTION1="VALUE")

assert cfg.DATABASE
assert cfg.ANY_OPTION1
```

### Environments

The module path may be set as an ENV variable:

```python
import os

from modconfig import Config

# Let's define an env var
os.environ["MODCONFIG"] = "myapp.config.production"

cfg = Config("env:MODCONFIG", "myapp.config.local")
assert cfg.DATABASE
```

### Custom environment variables

Any option may be overridden with an ENV variable. Values are parsed as JSON
when possible, so dicts and lists work; anything else stays a string.

ENV variables for options that do not exist in the config are ignored.

To pick up overrides only for your app, give them a prefix:

```python
cfg = Config("myapp.config.production", config_config={"env_prefix": "APP_"})
# APP_DATABASE overrides DATABASE, DEMOENV is ignored
```

The meta options of the config itself (`env_prefix`, `update_from_env`) are
passed through `config_config`.

See [tests.py](https://github.com/klen/modconfig/blob/develop/tests.py) for
more examples.

## Limitations

Configuration modules are Python code, so importing one executes it. Keep them
as trusted as the application itself.

Only the first importable module in the list is used. The rest are fallbacks for
when an earlier module is missing, not layers that get merged.

ENV overrides apply only to options that already exist in the config; unknown
variables are ignored rather than added.

Because an option keeps the type of its first value, replacing an `int` with a
`str` later does not work: the string is converted back to an `int` or dropped.

## Bug tracker

If you have any suggestions, bug reports or annoyances please report them to
the issue tracker at <https://github.com/klen/modconfig/issues>.

## Contributing

Development of the project happens at
<https://github.com/klen/modconfig>.

## License

Licensed under a [MIT license](https://opensource.org/licenses/MIT).
