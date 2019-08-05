# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class RadioItems(Component):
    """A RadioItems component.
RadioItems is a component that encapsulates several radio item inputs.
The values and labels of the RadioItems is specified in the `options`
property and the seleced item is specified with the `value` property.
Each radio item is rendered as an input with a surrounding label.

Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- options (dict; optional): An array of options. options has the following type: list of dicts containing keys 'label', 'value', 'disabled'.
Those keys have the following types:
  - label (string | number; required): The radio item's label
  - value (string | number; required): The value of the radio item. This value
corresponds to the items specified in the
`value` property.
  - disabled (boolean; optional): If true, this radio item is disabled and can't be clicked on.
- value (string | number; optional): The currently selected value
- style (dict; optional): The style of the container (div)
- className (string; optional): The class of the container (div)
- inputStyle (dict; optional): The style of the <input> radio element
- inputClassName (string; default ''): The class of the <input> radio element
- labelStyle (dict; optional): The style of the <label> that wraps the radio input
 and the option's label
- labelClassName (string; default ''): The class of the <label> that wraps the radio input
 and the option's label
- loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, options=Component.UNDEFINED, value=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, inputStyle=Component.UNDEFINED, inputClassName=Component.UNDEFINED, labelStyle=Component.UNDEFINED, labelClassName=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'options', 'value', 'style', 'className', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName', 'loading_state']
        self._type = 'RadioItems'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'options', 'value', 'style', 'className', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(RadioItems, self).__init__(**args)
