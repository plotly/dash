# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class RangeSlider(Component):
    """A RangeSlider component.
    A double slider with two handles.
    Used for specifying a range of numerical values.

    Keyword arguments:

    - min (number; optional):
        Minimum allowed value of the slider.

    - max (number; optional):
        Maximum allowed value of the slider.

    - step (number; optional):
        Value by which increments or decrements are made.

    - marks (dict; optional):
        Marks on the slider. The key determines the position (a number),
        and the value determines what will show. If you want to set the
        style of a specific mark point, the value should be an object
        which contains style and label properties.

        `marks` is a dict with strings as keys and values of type string |
        dict with keys:

        - label (string; optional)

        - style (dict; optional)

    - value (list of numbers; optional):
        The value of the input.

    - drag_value (list of numbers; optional):
        The value of the input during a drag.

    - allowCross (boolean; optional):
        allowCross could be set as True to allow those handles to cross.

    - pushable (boolean | number; optional):
        pushable could be set as True to allow pushing of surrounding
        handles when moving an handle. When set to a number, the number
        will be the minimum ensured distance between handles.

    - disabled (boolean; optional):
        If True, the handles can't be moved.

    - count (number; optional):
        Determine how many ranges to render, and multiple handles will be
        rendered (number + 1).

    - dots (boolean; optional):
        When the step value is greater than 1, you can set the dots to
        True if you want to render the slider with dots.

    - included (boolean; optional):
        If the value is True, it means a continuous value is included.
        Otherwise, it is an independent value.

    - tooltip (dict; optional):
        Configuration for tooltips describing the current slider values.

        `tooltip` is a dict with keys:

        - always_visible (boolean; optional):
            Determines whether tooltips should always be visible (as
            opposed to the default, visible on hover).

        - placement (a value equal to: 'left', 'right', 'top', 'bottom', 'topLeft', 'topRight', 'bottomLeft', 'bottomRight'; optional):
            Determines the placement of tooltips See
            https://github.com/react-component/tooltip#api top/bottom{*}
            sets the _origin_ of the tooltip, so e.g. `topLeft` will in
            reality appear to be on the top right of the handle.

    - updatemode (a value equal to: 'mouseup', 'drag'; default 'mouseup'):
        Determines when the component should update its `value` property.
        If `mouseup` (the default) then the slider will only trigger its
        value when the user has finished dragging the slider. If `drag`,
        then the slider will update its value continuously as it is being
        dragged. Note that for the latter case, the `drag_value` property
        could be used instead.

    - vertical (boolean; optional):
        If True, the slider will be vertical.

    - verticalHeight (number; default 400):
        The height, in px, of the slider if it is vertical.

    - className (string; optional):
        Additional CSS class for the root DOM node.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

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

    - persistence (boolean | string | number; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (list of a value equal to: 'value's; default ['value']):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit."""

    @_explicitize_args
    def __init__(
        self,
        min=Component.UNDEFINED,
        max=Component.UNDEFINED,
        step=Component.UNDEFINED,
        marks=Component.UNDEFINED,
        value=Component.UNDEFINED,
        drag_value=Component.UNDEFINED,
        allowCross=Component.UNDEFINED,
        pushable=Component.UNDEFINED,
        disabled=Component.UNDEFINED,
        count=Component.UNDEFINED,
        dots=Component.UNDEFINED,
        included=Component.UNDEFINED,
        tooltip=Component.UNDEFINED,
        updatemode=Component.UNDEFINED,
        vertical=Component.UNDEFINED,
        verticalHeight=Component.UNDEFINED,
        className=Component.UNDEFINED,
        id=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        persistence=Component.UNDEFINED,
        persisted_props=Component.UNDEFINED,
        persistence_type=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "min",
            "max",
            "step",
            "marks",
            "value",
            "drag_value",
            "allowCross",
            "pushable",
            "disabled",
            "count",
            "dots",
            "included",
            "tooltip",
            "updatemode",
            "vertical",
            "verticalHeight",
            "className",
            "id",
            "loading_state",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self._type = "RangeSlider"
        self._namespace = "dash_core_components"
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "min",
            "max",
            "step",
            "marks",
            "value",
            "drag_value",
            "allowCross",
            "pushable",
            "disabled",
            "count",
            "dots",
            "included",
            "tooltip",
            "updatemode",
            "vertical",
            "verticalHeight",
            "className",
            "id",
            "loading_state",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in []:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(RangeSlider, self).__init__(**args)
