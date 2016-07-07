import os
import dash as _dash
import sys as _sys

current_path = os.path.dirname(os.path.abspath(__file__))

_dash.development.component_loader.load_components(
    os.path.join(current_path, '../lib/metadata.json'),
    ['content', 'id', 'key', 'className', 'style', 'dependencies'],
    globals(),
    _sys._getframe(1).f_globals.get('__name__', '__main__')
)
