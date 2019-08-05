# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class RangeSlider(Component):
    """A RangeSlider component.
A double slider with two handles.
Used for specifying a range of numerical values.

Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- marks (dict; optional): Marks on the slider.
The key determines the position (a number),
and the value determines what will show.
If you want to set the style of a specific mark point,
the value should be an object which
contains style and label properties. marks has the following type: dict with strings as keys and values of type string | dict containing keys 'label', 'style'.
Those keys have the following types:
  - label (string; optional)
  - style (dict; optional)
- value (list of numbers; optional): The value of the input
- allowCross (boolean; optional): allowCross could be set as true to allow those handles to cross.
- className (string; optional): Additional CSS class for the root DOM node
- count (number; optional): Determine how many ranges to render, and multiple handles
will be rendered (number + 1).
- disabled (boolean; optional): If true, the handles can't be moved.
- dots (boolean; optional): When the step value is greater than 1,
you can set the dots to true if you want to
render the slider with dots.
- included (boolean; optional): If the value is true, it means a continuous
value is included. Otherwise, it is an independent value.
- min (number; optional): Minimum allowed value of the slider
- max (number; optional): Maximum allowed value of the slider
- pushable (boolean | number; optional): pushable could be set as true to allow pushing of
surrounding handles when moving an handle.
When set to a number, the number will be the
minimum ensured distance between handles.
- tooltip (dict; optional): tooltip has the following type: dict containing keys 'always_visible', 'placement'.
Those keys have the following types:
  - always_visible (boolean; optional): Determines whether tooltips should always be visible
(as opposed to the default, visible on hover)
  - placement (a value equal to: 'left', 'right', 'top', 'bottom', 'topLeft', 'topRight', 'bottomLeft', 'bottomRight'; optional): Determines the placement of tooltips
See https://github.com/react-component/tooltip#api
top/bottom{*} sets the _origin_ of the tooltip, so e.g. `topLeft` will
in reality appear to be on the top right of the handle
- step (number; optional): Value by which increments or decrements are made
- vertical (boolean; optional): If true, the slider will be vertical
- updatemode (a value equal to: 'mouseup', 'drag'; default 'mouseup'): Determines when the component should update
its value. If `mouseup`, then the slider
will only trigger its value when the user has
finished dragging the slider. If `drag`, then
the slider will update its value continuously
as it is being dragged.
Only use `drag` if your updates are fast.
- loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, marks=Component.UNDEFINED, value=Component.UNDEFINED, allowCross=Component.UNDEFINED, className=Component.UNDEFINED, count=Component.UNDEFINED, disabled=Component.UNDEFINED, dots=Component.UNDEFINED, included=Component.UNDEFINED, min=Component.UNDEFINED, max=Component.UNDEFINED, pushable=Component.UNDEFINED, tooltip=Component.UNDEFINED, step=Component.UNDEFINED, vertical=Component.UNDEFINED, updatemode=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'marks', 'value', 'allowCross', 'className', 'count', 'disabled', 'dots', 'included', 'min', 'max', 'pushable', 'tooltip', 'step', 'vertical', 'updatemode', 'loading_state']
        self._type = 'RangeSlider'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'marks', 'value', 'allowCross', 'className', 'count', 'disabled', 'dots', 'included', 'min', 'max', 'pushable', 'tooltip', 'step', 'vertical', 'updatemode', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(RangeSlider, self).__init__(**args)
