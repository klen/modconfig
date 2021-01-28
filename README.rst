modconfig
#########

.. _description:

**modconfig** -- Simple hierarchic configuration manager for apps

.. _badges:

.. image:: https://github.com/klen/modconfig/workflows/tests/badge.svg
    :target: https://github.com/klen/modconfig/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/modconfig
    :target: https://pypi.org/project/modconfig/
    :alt: PYPI Version

.. _motivation:

Motivation
==========

Applications (especially web services) often require certain configuration
options to depend on the environment an application runs in (development,
testing, production, etc.). For instance, a database address config option may
default to a local database server during development, a mock database server
during testing, and yet another database server during production. It may also
need to be customizable via an environment variable. `modconfig` approaches
scenarios like this and, allows to specify default configuration options for
various environments and optionally override them by custom environment
variables.

`modconfig` uses python modules for keep the configuration options. You are
not locked by format (json, yaml, ini) restrictions and able to use any python
statements/modules to tune your configuration as a pro. It keeps the
flexability and make your configuration very declarative without any magic.

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 3.6

.. _installation:

Installation
=============

**modconfig** should be installed using pip: ::

    pip install modconfig

.. _usage:

Usage
=====

For example you have the structure in your app:

.. code::

   |- myapp/
   |  |- __init__.py
   |  |- config/
   |  |  |- __init__.py
   |  |  |- defaults.py
   |  |  |- production.py
   |  |  |- stage.py
   |  |  |- tests.py
   |  | ...

See https://github.com/klen/modconfig/tree/develop/example as a simple reference.

Initialize the config in your app and use it anywhere:

.. code:: python

   from modconfig import Config

   cfg = Config('myapp.config.production', ANY_OPTION1="VALUE", ANY_OPTION2="VALUE")  # instead an import path it could be the module itself

   assert cfg.DATABASE
   assert cfg.ANY_OPTION1


Fallbacks
---------

If you provide a several modules, `modconfig` will be using the first available:

.. code:: python

   from modconfig import Config

   cfg = Config('myapp.config.local', 'myapp.config.production', ANY_OPTION1="VALUE")

   assert cfg.DATABASE
   assert cfg.ANY_OPTION1


Enviroments
-----------

The module path may be set as ENV variable:

.. code:: python

   import os
   from modconfig import Config

   # Let's define an env var
   os.environ['MODCONFIG'] = 'myapp.config.production'

   cfg = Config('env:MODCONFIG', 'myapp.config.local')
   assert cfg.DATABASE


Custom Environment Variables
----------------------------

Any option may be redifened with ENV variables. By default the `modconfig`
tries to parse value as a JSON which allows us to set complex values (dict,
list, etc). If value is not JSON it would be parsed as str.

Any ENV variables which names are not contained in source module would be
ignored.

See https://github.com/klen/modconfig/tree/develop/tests.py for more examples.

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/modconfig/issues

.. _contributing:

Contributing
============

Development of the project happens at: https://github.com/klen/modconfig

.. _license:

License
========

Licensed under a `MIT license`_.


.. _links:


.. _klen: https://github.com/klen

.. _MIT license: http://opensource.org/licenses/MIT

