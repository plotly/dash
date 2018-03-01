import os as _os
import sys as _sys
import dash as _dash
from .version import __version__

_current_path = _os.path.dirname(_os.path.abspath(__file__))

_components = _dash.development.component_loader.load_components(
    _os.path.join(_current_path, 'metadata.json'),
    'dash_core_components'
)

_this_module = _sys.modules[__name__]

_js_dist = [
    {
        'external_url': 'https://cdn.plot.ly/plotly-1.34.0.min.js',
        'relative_package_path': 'plotly-1.34.0.min.js',
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


for component in _components:
    setattr(_this_module, component.__name__, component)
    setattr(component, '_js_dist', _js_dist)
    setattr(component, '_css_dist', _css_dist)
