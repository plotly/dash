import json
import os as _os
import sys as _sys
import dash as _dash

from ._imports_ import *  # noqa: F401, F403, E402
from ._imports_ import __all__  # noqa: E402
from .express import (  # noqa: F401, E402
    send_bytes,
    send_data_frame,
    send_file,
    send_string,
)

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


_this_module = "dash_core_components"

async_resources = [
    "datepicker",
    "dropdown",
    "graph",
    "highlight",
    "markdown",
    "slider",
    "upload",
]

_js_dist = []

_js_dist.extend(
    [
        {
            "relative_package_path": "dcc/async-{}.js".format(async_resource),
            "external_url": (
                "https://unpkg.com/dash-core-components@{}"
                "/dash_core_components/async-{}.js"
            ).format(__version__, async_resource),
            "namespace": "dash",
            "async": True,
        }
        for async_resource in async_resources
    ]
)

_js_dist.extend(
    [
        {
            "relative_package_path": "dcc/async-{}.js.map".format(async_resource),
            "external_url": (
                "https://unpkg.com/dash-core-components@{}"
                "/dash_core_components/async-{}.js.map"
            ).format(__version__, async_resource),
            "namespace": "dash",
            "dynamic": True,
        }
        for async_resource in async_resources
    ]
)

_js_dist.extend(
    [
        {
            "relative_package_path": "dcc/{}.js".format(_this_module),
            "external_url": (
                "https://unpkg.com/dash-core-components@{}"
                "/dash_core_components/dash_core_components.js"
            ).format(__version__),
            "namespace": "dash",
        },
        {
            "relative_package_path": "dcc/{}.js.map".format(_this_module),
            "external_url": (
                "https://unpkg.com/dash-core-components@{}"
                "/dash_core_components/dash_core_components.js.map"
            ).format(__version__),
            "namespace": "dash",
            "dynamic": True,
        },
        {
            "relative_package_path": "dcc/{}-shared.js".format(_this_module),
            "external_url": (
                "https://unpkg.com/dash-core-components@{}"
                "/dash_core_components/dash_core_components-shared.js"
            ).format(__version__),
            "namespace": "dash",
        },
        {
            "relative_package_path": "dcc/{}-shared.js.map".format(_this_module),
            "external_url": (
                "https://unpkg.com/dash-core-components@{}"
                "/dash_core_components/dash_core_components-shared.js.map"
            ).format(__version__),
            "namespace": "dash",
            "dynamic": True,
        },
        {
            "relative_package_path": "dcc/plotly.min.js",
            "external_url": (
                "https://unpkg.com/dash-core-components@{}"
                "/dash_core_components/plotly.min.js"
            ).format(__version__),
            "namespace": "dash",
            "async": "eager",
        },
        {
            "relative_package_path": "dcc/async-plotlyjs.js",
            "external_url": (
                "https://unpkg.com/dash-core-components@{}"
                "/dash_core_components/async-plotlyjs.js"
            ).format(__version__),
            "namespace": "dash",
            "async": "lazy",
        },
        {
            "relative_package_path": "dcc/async-plotlyjs.js.map",
            "external_url": (
                "https://unpkg.com/dash-core-components@{}"
                "/dash_core_components/async-plotlyjs.js.map"
            ).format(__version__),
            "namespace": "dash",
            "dynamic": True,
        },
    ]
)

for _component in __all__:
    setattr(locals()[_component], "_js_dist", _js_dist)
