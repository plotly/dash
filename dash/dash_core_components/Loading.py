# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Loading(Component):
    """A Loading component.
A Loading component that wraps any other component and displays a spinner until the wrapped component has rendered.

Keyword arguments:

- children (list of a list of or a singular dash component, string or numbers | a list of or a singular dash component, string or number; optional):
    Array that holds components to render.

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- className (string; optional):
    Additional CSS class for the spinner root DOM node.

- color (string; default '#119DFF'):
    Primary colour used for the loading spinners.

- debug (boolean; optional):
    If True, the spinner will display the component_name and prop_name
    while loading.

- fullscreen (boolean; optional):
    Boolean that makes the spinner display full-screen.

- loading_state (dict; optional):
    Object that holds the loading state object coming from
    dash-renderer.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- parent_className (string; optional):
    Additional CSS class for the outermost dcc.Loading parent div DOM
    node.

- parent_style (dict; optional):
    Additional CSS styling for the outermost dcc.Loading parent div
    DOM node.

- style (dict; optional):
    Additional CSS styling for the spinner root DOM node.

- type (a value equal to: 'graph', 'cube', 'circle', 'dot', 'default'; default 'default'):
    Property that determines which spinner to show one of 'graph',
    'cube', 'circle', 'dot', or 'default'."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, type=Component.UNDEFINED, fullscreen=Component.UNDEFINED, debug=Component.UNDEFINED, className=Component.UNDEFINED, parent_className=Component.UNDEFINED, style=Component.UNDEFINED, parent_style=Component.UNDEFINED, color=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'color', 'debug', 'fullscreen', 'loading_state', 'parent_className', 'parent_style', 'style', 'type']
        self._type = 'Loading'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'color', 'debug', 'fullscreen', 'loading_state', 'parent_className', 'parent_style', 'style', 'type']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Loading, self).__init__(children=children, **args)
