import dash as _dash
import sys as _sys

_dash.development.component_loader.load_components(
    '../lib/metadata.json',
    ['content', 'id', 'key', 'className', 'style', 'dependencies'],
    globals(),
    _sys._getframe(1).f_globals.get('__name__', '__main__')
)
