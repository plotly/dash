"""Dash Core Components"""

__version__ = "2.0.0"

# Required attributes for Dash initialization
_js_dist = []
_css_dist = []

# Import or create minimal components as needed
from dash.development.base_component import Component

class Input(Component):
    def __init__(self, value=None, id=None, type=None, **kwargs):
        self._prop_names = ['value', 'id', 'type'] + list(kwargs.keys())
        self._type = 'Input'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes = ['data-', 'aria-']
        if id is not None:
            kwargs['id'] = id
        if value is not None:
            kwargs['value'] = value
        if type is not None:
            kwargs['type'] = type
        super().__init__(**kwargs)

__all__ = ['Input', '_js_dist', '_css_dist']
