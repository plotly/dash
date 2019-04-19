# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Dropdown(Component):
    """A Dropdown component.
Dropdown is an interactive dropdown element for selecting one or more
items.
The values and labels of the dropdown items are specified in the `options`
property and the selected item(s) are specified with the `value` property.

Use a dropdown when you have many options (more than 5) or when you are
constrained for space. Otherwise, you can use RadioItems or a Checklist,
which have the benefit of showing the users all of the items at once.

Keyword arguments:
- id (string; optional)
- options (list; optional): An array of options
- value (string | list | number | list; optional): The value of the input. If `multi` is false (the default)
then value is just a string that corresponds to the values
provided in the `options` property. If `multi` is true, then
multiple values can be selected at once, and `value` is an
array of items with values corresponding to those in the
`options` prop.
- className (string; optional): className of the dropdown element
- clearable (boolean; optional): Whether or not the dropdown is "clearable", that is, whether or
not a small "x" appears on the right of the dropdown that removes
the selected value.
- disabled (boolean; optional): If true, the option is disabled
- multi (boolean; optional): If true, the user can select multiple values
- placeholder (string; optional): The grey, default text shown when no option is selected
- searchable (boolean; optional): Whether to enable the searching feature or not
- style (dict; optional)
- loading_state (optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, options=Component.UNDEFINED, value=Component.UNDEFINED, className=Component.UNDEFINED, clearable=Component.UNDEFINED, disabled=Component.UNDEFINED, multi=Component.UNDEFINED, placeholder=Component.UNDEFINED, searchable=Component.UNDEFINED, style=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'options', 'value', 'className', 'clearable', 'disabled', 'multi', 'placeholder', 'searchable', 'style', 'loading_state']
        self._type = 'Dropdown'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'options', 'value', 'className', 'clearable', 'disabled', 'multi', 'placeholder', 'searchable', 'style', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Dropdown, self).__init__(**args)
