import re
from os import path as op

from setuptools import setup


PROJECT = 'modconfig'


def _read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''


meta = _read('%s.py' % PROJECT)

setup(
    name=PROJECT,
    version=re.search(r'^__version__\s*=\s*"(.*)"', meta, re.M).group(1),
    license=re.search(r'^__license__\s*=\s*"(.*)"', meta, re.M).group(1),
    description="Simple hierarchic configuration manager for apps",
    long_description=_read('README.rst'),

    py_modules=['modconfig'],

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    homepage="https://github.com/klen/modconfig",
    repository="https://github.com/klen/modconfig",
    keywords="config settings configuration",

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Topic :: Software Development :: Libraries",
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
