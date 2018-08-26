"""This package provides the core React component suite for Dash."""

from __future__ import print_function as _

import os as _os
import sys as _sys
import dash as _dash

from .version import __version__

# Module imports trigger a dash.development import, need to check this first
if not hasattr(_dash, 'development'):
    print("Dash was not successfully imported. Make sure you don't have a file "
          "named \n'dash.py' in your current directory.", file=_sys.stderr)
    _sys.exit(1)

# Must update to dash>=0.23.1 to use this version of dash-core-components
if not hasattr(_dash.development.base_component, '_explicitize_args'):
    print("Please update the `dash` module to >= 0.23.1 to use this "
          "version of dash_core_components.\n"
          "You are using version {:s}".format(_dash.version.__version__),
          file=_sys.stderr)
    _sys.exit(1)


from ._imports_ import *
from ._imports_ import __all__


_current_path = _os.path.dirname(_os.path.abspath(__file__))


_this_module = _sys.modules[__name__]


_js_dist = [
    {
        'external_url': 'https://cdn.plot.ly/plotly-1.40.1.min.js',
        'relative_package_path': 'plotly-1.40.1.min.js',
        'namespace': 'dash_core_components'
    },
    {
        'relative_package_path': 'bundle.js',
        'external_url': (
            'https://unpkg.com/dash-core-components@{}'
            '/dash_core_components/bundle.js'
        ).format(__version__),
        'namespace': 'dash_core_components'
    }
]


_css_dist = [
    {
        'relative_package_path': [
            'rc-slider@6.1.2.css',
            'react-select@1.0.0-rc.3.min.css',
            'react-virtualized@9.9.0.css',
            'react-virtualized-select@3.1.0.css',
            'react-dates@12.3.0.css'
        ],
        'external_url': [
            'https://unpkg.com/react-select@1.0.0-rc.3/dist/react-select.min.css',
            'https://unpkg.com/react-virtualized@9.9.0/styles.css',
            'https://unpkg.com/react-virtualized-select@3.1.0/styles.css',
            'https://unpkg.com/rc-slider@6.1.2/assets/index.css',
            'https://unpkg.com/dash-core-components@{}/dash_core_components/react-dates@12.3.0.css'.format(__version__)
        ],
        'namespace': 'dash_core_components'
    }
]


for _component in __all__:
    setattr(locals()[_component], '_js_dist', _js_dist)
    setattr(locals()[_component], '_css_dist', _css_dist)
