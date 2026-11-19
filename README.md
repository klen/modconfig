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

### Fallbacks

If you provide several modules, `modconfig` will be using the first available:

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

Any option may be redefined with ENV variables. By default `modconfig` tries to
parse the value as JSON, which allows us to set complex values (dict, list,
etc). If the value is not JSON it is parsed as a string.

Any ENV variables which names are not contained in the source module are
ignored.

See [tests.py](https://github.com/klen/modconfig/blob/develop/tests.py) for
more examples.

## Bug tracker

If you have any suggestions, bug reports or annoyances please report them to
the issue tracker at <https://github.com/klen/modconfig/issues>.

## Contributing

Development of the project happens at
<https://github.com/klen/modconfig>.

## License

Licensed under a [MIT license](https://opensource.org/licenses/MIT).
