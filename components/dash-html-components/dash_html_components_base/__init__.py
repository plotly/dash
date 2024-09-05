"""Vanilla HTML components for Dash"""

from ._imports_ import *  # noqa: E402, F401, F403
from ._imports_ import __all__  # noqa: E402

import json
import os as _os
import sys as _sys
import dash as _dash

_basepath = _os.path.dirname(__file__)
_filepath = _os.path.abspath(_os.path.join(_basepath, "package-info.json"))
with open(_filepath) as f:
    package = json.load(f)

package_name = package["name"].replace(" ", "_").replace("-", "_")
__version__ = package["version"]


# Module imports trigger a dash.development import, need to check this first
if not hasattr(_dash, "__plotly_dash") and not hasattr(_dash, "development"):
    print(
        "Dash was not successfully imported. Make sure you don't have a file "
        "named \n'dash.py' in your current directory.",
        file=_sys.stderr,
    )
    _sys.exit(1)

_current_path = _os.path.dirname(_os.path.abspath(__file__))


_this_module = "dash_html_components"

_js_dist = [
    {
        "relative_package_path": "html/{}.min.js".format(_this_module),
        "external_url": (
            "https://unpkg.com/dash-html-components@{}"
            "/dash_html_components/dash_html_components.min.js"
        ).format(__version__),
        "namespace": "dash",
    },
    {
        "relative_package_path": "html/{}.min.js.map".format(_this_module),
        "external_url": (
            "https://unpkg.com/dash-html-components@{}"
            "/dash_html_components/dash_html_components.min.js.map"
        ).format(__version__),
        "namespace": "dash",
        "dynamic": True,
    },
]

_css_dist = []


for _component in __all__:
    setattr(locals()[_component], "_js_dist", _js_dist)
    setattr(locals()[_component], "_css_dist", _css_dist)
