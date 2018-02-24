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

_DEFAULT_REACT_VERSION = '15.4.2'
_REACT_VERSION_TYPES = {'15.4.2', '16.2.0'}
_REACT_VERSION_TO_URLS = {
    '15.4.2': {
        'external_url': [
            'https://unpkg.com/react@15.4.2/dist/react.min.js',
            'https://unpkg.com/react-dom@15.4.2/dist/react-dom.min.js'
        ],
        'relative_package_path': [
            'react@15.4.2.min.js',
            'react-dom@15.4.2.min.js'
        ],
    },
    '16.2.0': {
        'external_url': [
            'https://unpkg.com/react@16.2.0/umd/react.production.min.js',
            'https://unpkg.com/react-dom@16.2.0/umd/react-dom.production.min.js'
        ],
        'relative_package_path': [
            'react@16.2.0.production.min.js',
            'react-dom@16.2.0.production.min.js'
        ],
    }
}


def _set_react_version(react_version):
    """
    Update the version of React in _js_dist_dependencies served by dash-renderer to the client

    Example:
    ```
    import dash_renderer

    # Set the react version before setting up the Dash application
    dash_renderer._set_react_version('16.2.0')

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
        'relative_package_path': 'bundle.js',
        "external_url": (
            'https://unpkg.com/dash-renderer@{}'
            '/dash_renderer/bundle.js'
        ).format(__version__),
        'namespace': 'dash_renderer'
    }
]
