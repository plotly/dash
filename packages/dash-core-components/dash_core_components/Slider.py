# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Slider(Component):
    """A Slider component.
A slider component with a single handle.

Keyword arguments:
- id (string; optional)
- marks (optional): Marks on the slider.
The key determines the position (a number),
and the value determines what will show.
If you want to set the style of a specific mark point,
the value should be an object which
contains style and label properties.. marks has the following type: dict with strings as keys and values of type string | dict containing keys 'label', 'style'.
Those keys have the following types:
  - label (string; optional)
  - style (dict; optional)
- value (number; optional): The value of the input
- className (string; optional): Additional CSS class for the root DOM node
- disabled (boolean; optional): If true, the handles can't be moved.
- dots (boolean; optional): When the step value is greater than 1,
you can set the dots to true if you want to
render the slider with dots.
- included (boolean; optional): If the value is true, it means a continuous
value is included. Otherwise, it is an independent value.
- min (number; optional): Minimum allowed value of the slider
- max (number; optional): Maximum allowed value of the slider
- step (number; optional): Value by which increments or decrements are made
- vertical (boolean; optional): If true, the slider will be vertical
- updatemode (a value equal to: 'mouseup', 'drag'; optional): Determines when the component should update
its value. If `mouseup`, then the slider
will only trigger its value when the user has
finished dragging the slider. If `drag`, then
the slider will update its value continuously
as it is being dragged.
Only use `drag` if your updates are fast.
- loading_state (optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, marks=Component.UNDEFINED, value=Component.UNDEFINED, className=Component.UNDEFINED, disabled=Component.UNDEFINED, dots=Component.UNDEFINED, included=Component.UNDEFINED, min=Component.UNDEFINED, max=Component.UNDEFINED, step=Component.UNDEFINED, vertical=Component.UNDEFINED, updatemode=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'marks', 'value', 'className', 'disabled', 'dots', 'included', 'min', 'max', 'step', 'vertical', 'updatemode', 'loading_state']
        self._type = 'Slider'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'marks', 'value', 'className', 'disabled', 'dots', 'included', 'min', 'max', 'step', 'vertical', 'updatemode', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Slider, self).__init__(**args)
