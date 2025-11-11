"""Dash HTML Components"""

__version__ = "2.0.0"

from dash.development.base_component import Component

# Manually define the HTML components we need for tests
class Div(Component):
    def __init__(self, children=None, id=None, **kwargs):
        self._prop_names = ['children', 'id'] + list(kwargs.keys())
        self._type = 'Div'
        self._namespace = 'dash_html_components'
        self._valid_wildcard_attributes = ['data-', 'aria-']
        # Only pass id if it's not None
        if id is not None:
            kwargs['id'] = id
        if children is not None:
            kwargs['children'] = children
        super().__init__(**kwargs)

class Button(Component):
    def __init__(self, children=None, id=None, n_clicks=None, **kwargs):
        self._prop_names = ['children', 'id', 'n_clicks'] + list(kwargs.keys())
        self._type = 'Button'
        self._namespace = 'dash_html_components'
        self._valid_wildcard_attributes = ['data-', 'aria-']
        # Only pass non-None values
        if id is not None:
            kwargs['id'] = id
        if children is not None:
            kwargs['children'] = children
        if n_clicks is not None:
            kwargs['n_clicks'] = n_clicks
        super().__init__(**kwargs)

__all__ = ['Div', 'Button']
