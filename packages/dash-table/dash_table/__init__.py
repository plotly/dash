from __future__ import print_function as _

import os as _os
import sys as _sys
import json

import dash as _dash

if not hasattr(_dash, 'development'):
    print('Dash was not successfully imported. '
          'Make sure you don\'t have a file '
          'named \n"dash.py" in your current directory.', file=_sys.stderr)
    _sys.exit(1)

_basepath = _os.path.dirname(__file__)
_filepath = _os.path.abspath(_os.path.join(_basepath, 'package.json'))
with open(_filepath) as f:
    package = json.load(f)

package_name = package['name'].replace(' ', '_').replace('-', '_')
__version__ = package['version']

_current_path = _os.path.dirname(_os.path.abspath(__file__))
_components = _dash.development.component_loader.load_components(
    _os.path.join(_current_path, 'metadata.json'),
    package_name
)

_this_module = _sys.modules[__name__]


_js_dist = [
    {
        'relative_package_path': 'bundle.js',
        'external_url': (
            'https://unpkg.com/dash_table'
            '/' + package_name + '/bundle.js'
        ).format(__version__),
        'namespace': package_name
    }
]

_css_dist = []


for _component in _components:
    setattr(_this_module, _component.__name__, _component)
    setattr(_component, '_js_dist', _js_dist)
    setattr(_component, '_css_dist', _css_dist)
