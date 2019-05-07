import sys

# For reasons that I don't fully understand,
# unless I include __file__ in here, the packaged version
# of this module will just be a .egg file, not a .egg folder.
# And if it's just a .egg file, it won't include the necessary
# dependencies from MANIFEST.in.
# Found the __file__ clue by inspecting the `python setup.py install`
# command in the dash_html_components package which printed out:
# `dash_html_components.__init__: module references __file__`
# TODO - Understand this better
from .version import __version__
__file__

_DEFAULT_REACT_VERSION = '16.8.6'
_REACT_VERSION_TYPES = {'16.8.6'}
_REACT_VERSION_TO_URLS = {
    '16.8.6': {
        'external_url': [
            'https://unpkg.com/react@16.8.6/umd/react.production.min.js',
            'https://unpkg.com/react-dom@16.8.6/umd/react-dom.production.min.js'
        ],
        'relative_package_path': [
            'react@16.8.6.min.js',
            'react-dom@16.8.6.min.js'
        ],
    }
}


def _set_react_version(react_version):
    """
    Update the version of React in _js_dist_dependencies served by dash-renderer to the client

    Example:
    ```
    import dash_renderer

    app = dash.Dash(...)
    ```

    :param str react_version: Version of React

    """
    assert react_version in _REACT_VERSION_TYPES

    _this_module = sys.modules[__name__]

    # Dash renderer's dependencies get loaded in a special order by the server:
    # React bundles first, the renderer bundle at the very end.
    setattr(_this_module, '_js_dist_dependencies', [{
        'external_url': _REACT_VERSION_TO_URLS[react_version]['external_url'],
        'relative_package_path': _REACT_VERSION_TO_URLS[react_version]['relative_package_path'],
        'namespace': 'dash_renderer'
    }])


_js_dist_dependencies = []
_set_react_version(_DEFAULT_REACT_VERSION)

_js_dist = [
    {
        'relative_package_path': '{}.min.js'.format(__name__),
        'dev_package_path': '{}.dev.js'.format(__name__),
        "external_url": (
            'https://unpkg.com/dash-renderer@{}'
            '/dash_renderer/dash_renderer.min.js'
        ).format(__version__),
        'namespace': 'dash_renderer'
    },
    {
        'relative_package_path': '{}.min.js.map'.format(__name__),
        'dev_package_path': '{}.dev.js.map'.format(__name__),
        "external_url": (
            'https://unpkg.com/dash-renderer@{}'
            '/dash_renderer/dash_renderer.min.js.map'
        ).format(__version__),
        'namespace': 'dash_renderer',
        'dynamic': True
    }
]
