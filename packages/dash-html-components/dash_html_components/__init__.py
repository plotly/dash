"""Vanilla HTML components for Dash"""

from __future__ import print_function as _

import os as _os
import sys as _sys
import dash as _dash

from .version import __version__

# Module imports trigger a dash.development import, need to check this first
if not hasattr(_dash, 'development'):
    print(
        "Dash was not successfully imported. Make sure you don't have a file "
        "named \n'dash.py' in your current directory.", file=_sys.stderr)
    _sys.exit(1)

# Must update to dash>=0.22.0 to use this version of dash-html-components
if not hasattr(_dash.development.base_component, '_explicitize_args'):
    print("Please update the `dash` module to >= 0.22.0 to use this "
          "version of dash_html_components.\n"
          "You are using version {:s}".format(_dash.version.__version__),
          file=_sys.stderr)
    _sys.exit(1)


from ._imports_ import *
from ._imports_ import __all__


_current_path = _os.path.dirname(_os.path.abspath(__file__))


_this_module = _sys.modules[__name__]


_js_dist = [
    {
        "relative_package_path": '{}.min.js'.format(__name__),
        "dev_package_path": '{}.dev.js'.format(__name__),
        "external_url": (
            "https://unpkg.com/dash-html-components@{}"
            "/dash_html_components/dash_html_components.min.js"
        ).format(__version__),
        "namespace": "dash_html_components"
    }
]

_css_dist = []


for _component in __all__:
    setattr(locals()[_component], '_js_dist', _js_dist)
    setattr(locals()[_component], '_css_dist', _css_dist)
