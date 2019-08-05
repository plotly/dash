# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Checklist(Component):
    """A Checklist component.
Checklist is a component that encapsulates several checkboxes.
The values and labels of the checklist are specified in the `options`
property and the checked items are specified with the `value` property.
Each checkbox is rendered as an input with a surrounding label.

Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- options (dict; optional): An array of options. options has the following type: list of dicts containing keys 'label', 'value', 'disabled'.
Those keys have the following types:
  - label (string | number; required): The checkbox's label
  - value (string | number; required): The value of the checkbox. This value
corresponds to the items specified in the
`value` property.
  - disabled (boolean; optional): If true, this checkbox is disabled and can't be clicked on.
- value (list of string | numbers; optional): The currently selected value
- className (string; optional): The class of the container (div)
- style (dict; optional): The style of the container (div)
- inputStyle (dict; optional): The style of the <input> checkbox element
- inputClassName (string; default ''): The class of the <input> checkbox element
- labelStyle (dict; optional): The style of the <label> that wraps the checkbox input
 and the option's label
- labelClassName (string; default ''): The class of the <label> that wraps the checkbox input
 and the option's label
- loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, options=Component.UNDEFINED, value=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, inputStyle=Component.UNDEFINED, inputClassName=Component.UNDEFINED, labelStyle=Component.UNDEFINED, labelClassName=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'options', 'value', 'className', 'style', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName', 'loading_state']
        self._type = 'Checklist'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'options', 'value', 'className', 'style', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Checklist, self).__init__(**args)
