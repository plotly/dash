import os as _os
import dash as _dash
import sys as _sys
from version import __version__

_current_path = _os.path.dirname(_os.path.abspath(__file__))

_components = _dash.development.component_loader.load_components(
    _os.path.join(_current_path, 'metadata.json'),
    ['content', 'id', 'key', 'className', 'style'],
    'dash_core_components'
)

_this_module = _sys.modules[__name__]

_js_dist = [
    {
        "relative_package_path": "bundle.js",
        "external_url": (
            "https://unpkg.com/dash-core-components@{}"
            "/dash_core_components/bundle.js"
        ).format(__version__)
    }
]

_css_dist = [
    {
        "relative_package_path": [
            "react-select@1.0.0-rc.3.min.css",
            "rc-slider@6.1.2.css"
        ],
        "external_url": [
            "https://unpkg.com/react-select@1.0.0-rc.3/dist/react-select.min.css",
            "https://unpkg.com/rc-slider@6.1.2/assets/index.css"
        ]
    }
]


for component in _components:
    setattr(_this_module, component.__name__, component)
    setattr(component, '_js_dist', _js_dist)
    setattr(component, '_css_dist', _css_dist)
