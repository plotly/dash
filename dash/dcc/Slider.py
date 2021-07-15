# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Slider(Component):
    """A Slider component.
    A slider component with a single handle.

    Keyword arguments:

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - className (string; optional):
        Additional CSS class for the root DOM node.

    - disabled (boolean; optional):
        If True, the handles can't be moved.

    - dots (boolean; optional):
        When the step value is greater than 1, you can set the dots to
        True if you want to render the slider with dots.

    - drag_value (number; optional):
        The value of the input during a drag.

    - included (boolean; optional):
        If the value is True, it means a continuous value is included.
        Otherwise, it is an independent value.

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

    - marks (dict; optional):
        Marks on the slider. The key determines the position (a number),
        and the value determines what will show. If you want to set the
        style of a specific mark point, the value should be an object
        which contains style and label properties.

        `marks` is a dict with strings as keys and values of type string |
        dict with keys:

        - label (string; optional)

        - style (dict; optional)

    - max (number; optional):
        Maximum allowed value of the slider.

    - min (number; optional):
        Minimum allowed value of the slider.

    - persisted_props (list of a value equal to: 'value's; default ['value']):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence (boolean | string | number; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit.

    - step (number; optional):
        Value by which increments or decrements are made.

    - tooltip (dict; optional):
        Configuration for tooltips describing the current slider value.

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
        dragged. If you want different actions during and after drag,
        leave `updatemode` as `mouseup` and use `drag_value` for the
        continuously updating value.

    - value (number; optional):
        The value of the input.

    - vertical (boolean; optional):
        If True, the slider will be vertical.

    - verticalHeight (number; default 400):
        The height, in px, of the slider if it is vertical."""

    @_explicitize_args
    def __init__(
        self,
        id=Component.UNDEFINED,
        marks=Component.UNDEFINED,
        value=Component.UNDEFINED,
        drag_value=Component.UNDEFINED,
        className=Component.UNDEFINED,
        disabled=Component.UNDEFINED,
        dots=Component.UNDEFINED,
        included=Component.UNDEFINED,
        min=Component.UNDEFINED,
        max=Component.UNDEFINED,
        tooltip=Component.UNDEFINED,
        step=Component.UNDEFINED,
        vertical=Component.UNDEFINED,
        verticalHeight=Component.UNDEFINED,
        updatemode=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        persistence=Component.UNDEFINED,
        persisted_props=Component.UNDEFINED,
        persistence_type=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "id",
            "className",
            "disabled",
            "dots",
            "drag_value",
            "included",
            "loading_state",
            "marks",
            "max",
            "min",
            "persisted_props",
            "persistence",
            "persistence_type",
            "step",
            "tooltip",
            "updatemode",
            "value",
            "vertical",
            "verticalHeight",
        ]
        self._type = "Slider"
        self._namespace = "dash_core_components"
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "id",
            "className",
            "disabled",
            "dots",
            "drag_value",
            "included",
            "loading_state",
            "marks",
            "max",
            "min",
            "persisted_props",
            "persistence",
            "persistence_type",
            "step",
            "tooltip",
            "updatemode",
            "value",
            "vertical",
            "verticalHeight",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in []:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(Slider, self).__init__(**args)
