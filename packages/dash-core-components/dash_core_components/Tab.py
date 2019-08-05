# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Tab(Component):
    """A Tab component.
Part of dcc.Tabs - this is the child Tab component used to render a tabbed page.
Its children will be set as the content of that tab, which if clicked will become visible.

Keyword arguments:
- children (a list of or a singular dash component, string or number; optional): The content of the tab - will only be displayed if this tab is selected
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- label (string; optional): The tab's label
- value (string; optional): Value for determining which Tab is currently selected
- disabled (boolean; default False): Determines if tab is disabled or not - defaults to false
- disabled_style (dict; default {
    color: '#d6d6d6',
}): Overrides the default (inline) styles when disabled
- disabled_className (string; optional): Appends a class to the Tab component when it is disabled.
- className (string; optional): Appends a class to the Tab component.
- selected_className (string; optional): Appends a class to the Tab component when it is selected.
- style (dict; optional): Overrides the default (inline) styles for the Tab component.
- selected_style (dict; optional): Overrides the default (inline) styles for the Tab component when it is selected.
- loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, label=Component.UNDEFINED, value=Component.UNDEFINED, disabled=Component.UNDEFINED, disabled_style=Component.UNDEFINED, disabled_className=Component.UNDEFINED, className=Component.UNDEFINED, selected_className=Component.UNDEFINED, style=Component.UNDEFINED, selected_style=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'label', 'value', 'disabled', 'disabled_style', 'disabled_className', 'className', 'selected_className', 'style', 'selected_style', 'loading_state']
        self._type = 'Tab'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'label', 'value', 'disabled', 'disabled_style', 'disabled_className', 'className', 'selected_className', 'style', 'selected_style', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Tab, self).__init__(children=children, **args)
