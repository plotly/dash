from __future__ import print_function as _

import os as _os
import sys as _sys
import json

import dash as _dash

# noinspection PyUnresolvedReferences
from ._imports_ import *
from ._imports_ import __all__

if not hasattr(_dash, 'development'):
    print('Dash was not successfully imported. '
          'Make sure you don\'t have a file '
          'named \n"dash.py" in your current directory.', file=_sys.stderr)
    _sys.exit(1)

_basepath = _os.path.dirname(__file__)
_filepath = _os.path.abspath(_os.path.join(_basepath, 'package-info.json'))
with open(_filepath) as f:
    package = json.load(f)

package_name = package['name'].replace(' ', '_').replace('-', '_')
__version__ = package['version']

_current_path = _os.path.dirname(_os.path.abspath(__file__))

_this_module = _sys.modules[__name__]


_js_dist = [
    {
        'relative_package_path': 'bundle.js',
        'external_url': (
            'https://unpkg.com/dash-table@{}/dash_table/bundle.js'
        ).format(__version__),
        'namespace': package_name
    },
    {
        'relative_package_path': 'bundle.js.map',
        'external_url': (
            'https://unpkg.com/dash-table@{}/dash_table/bundle.js.map'
        ).format(__version__),
        'namespace': package_name,
        'dynamic': True
    },
    {
        'relative_package_path': 'async~export.js',
        'external_url': (
            'https://unpkg.com/dash-table@{}/dash_table/async~export.js'
        ).format(__version__),
        'namespace': package_name,
        'async': True
    },
    {
        'relative_package_path': 'async~export.js.map',
        'external_url': (
            'https://unpkg.com/dash-table@{}/dash_table/async~export.js.map'
        ).format(__version__),
        'namespace': package_name,
        'dynamic': True
    },
    {
        'relative_package_path': 'async~table.js',
        'external_url': (
            'https://unpkg.com/dash-table@{}/dash_table/async~table.js'
        ).format(__version__),
        'namespace': package_name,
        'async': True
    },
    {
        'relative_package_path': 'async~table.js.map',
        'external_url': (
            'https://unpkg.com/dash-table@{}/dash_table/async~table.js.map'
        ).format(__version__),
        'namespace': package_name,
        'dynamic': True
    }
]

_css_dist = []


for _component in __all__:
    setattr(locals()[_component], '_js_dist', _js_dist)
    setattr(locals()[_component], '_css_dist', _css_dist)
