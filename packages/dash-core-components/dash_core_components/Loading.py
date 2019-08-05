# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Loading(Component):
    """A Loading component.
A Loading component that wraps any other component and displays a spinner until the wrapped component has rendered.

Keyword arguments:
- children (list of a list of or a singular dash component, string or numbers | a list of or a singular dash component, string or number; optional): Array that holds components to render
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- type (a value equal to: 'graph', 'cube', 'circle', 'dot', 'default'; default 'default'): Property that determines which spinner to show - one of 'graph', 'cube', 'circle', 'dot', or 'default'.
- fullscreen (boolean; optional): Boolean that determines if the loading spinner will be displayed full-screen or not
- debug (boolean; optional): Boolean that determines if the loading spinner will display the status.prop_name and component_name
- className (string; optional): Additional CSS class for the root DOM node
- style (dict; optional): Additional CSS styling for the root DOM node
- color (string; default '#119DFF'): Primary colour used for the loading spinners
- loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, type=Component.UNDEFINED, fullscreen=Component.UNDEFINED, debug=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, color=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'type', 'fullscreen', 'debug', 'className', 'style', 'color', 'loading_state']
        self._type = 'Loading'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'type', 'fullscreen', 'debug', 'className', 'style', 'color', 'loading_state']
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
