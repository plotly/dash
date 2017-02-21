import os as _os
import dash as _dash
import sys as _sys
from version import __version__

_current_path = _os.path.dirname(_os.path.abspath(__file__))

_components = _dash.development.component_loader.load_components(
    _os.path.join(_current_path, 'metadata.json'),
    ['content', 'id', 'key', 'className', 'style'],
    'dash_html_components'
)

_this_module = _sys.modules[__name__]

for component in _components:
    setattr(_this_module, component.__name__, component)
