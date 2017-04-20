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

# Dash renderer's dependencies get loaded in a special order by the server:
# React bundles first, the renderer bundle at the very end.
_js_dist_dependencies = [
    {
        'external_url': [
            'https://unpkg.com/react@15.4.2/dist/react.min.js',
            'https://unpkg.com/react-dom@15.4.2/dist/react-dom.min.js'
        ],
        'relative_package_path': [
            'react@15.4.2.min.js',
            'react-dom@15.4.2.min.js'
        ],
        'namespace': 'dash_renderer'
    }
]

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
