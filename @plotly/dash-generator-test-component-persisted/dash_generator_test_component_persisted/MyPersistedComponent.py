# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class MyPersistedComponent(Component):
    """A MyPersistedComponent component.
MyComponent description

Keyword arguments:
- id (string; optional): The id of the component
- value (string; default ''): The value to display
- value2 (string; default ''): The value to display
- persistence (boolean | string | number; optional)
- persisted_props (list of a value equal to: 'value', 'value2's; default ['value', 'value2']): Properties whose user interactions will persist after refreshing the
component or the page.
- persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'): Where persisted user changes will be stored:
memory: only kept in memory, reset on page refresh.
local: window.localStorage, data is kept after the browser quit.
session: window.sessionStorage, data is cleared once the browser quit."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, value=Component.UNDEFINED, value2=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'value', 'value2', 'persistence', 'persisted_props', 'persistence_type']
        self._type = 'MyPersistedComponent'
        self._namespace = 'dash_generator_test_component_persisted'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'value', 'value2', 'persistence', 'persisted_props', 'persistence_type']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(MyPersistedComponent, self).__init__(**args)
