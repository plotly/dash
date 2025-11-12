# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class Slider(Component):
    """A Slider component.
    A slider component with a single handle.

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

    - value (number; optional):
        The value of the input.

    - drag_value (number; optional):
        The value of the input during a drag.

    - disabled (boolean; optional):
        If True, the handles can't be moved.

    - dots (boolean; optional):
        When the step value is greater than 1, you can set the dots to
        True if you want to render the slider with dots.

    - included (boolean; optional):
        If the value is True, it means a continuous value is included.
        Otherwise, it is an independent value.

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

        - template (string; optional):
            Template string to display the tooltip in. Must contain
            `{value}`, which will be replaced with either the default
            string representation of the value or the result of the
            transform function if there is one.

        - style (dict; optional):
            Custom style for the tooltip.

        - transform (string; optional):
            Reference to a function in the `window.dccFunctions`
            namespace. This can be added in a script in the asset folder.
            For example, in `assets/tooltip.js`: ``` window.dccFunctions =
            window.dccFunctions || {}; window.dccFunctions.multByTen =
            function(value) {     return value * 10; } ``` Then in the
            component `tooltip={'transform': 'multByTen'}`.

    - updatemode (a value equal to: 'mouseup', 'drag'; default 'mouseup'):
        Determines when the component should update its `value` property.
        If `mouseup` (the default) then the slider will only trigger its
        value when the user has finished dragging the slider. If `drag`,
        then the slider will update its value continuously as it is being
        dragged. If you want different actions during and after drag,
        leave `updatemode` as `mouseup` and use `drag_value` for the
        continuously updating value.

    - vertical (boolean; optional):
        If True, the slider will be vertical.

    - verticalHeight (number; default 400):
        The height, in px, of the slider if it is vertical.

    - reverse (boolean; default False):
        If the value is True, it means the component is rendered reverse.

    - className (string; optional):
        Additional CSS class for the root DOM node.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

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

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Slider"
    Marks = TypedDict("Marks", {"label": NotRequired[str], "style": NotRequired[dict]})

    Tooltip = TypedDict(
        "Tooltip",
        {
            "always_visible": NotRequired[bool],
            "placement": NotRequired[
                Literal[
                    "left",
                    "right",
                    "top",
                    "bottom",
                    "topLeft",
                    "topRight",
                    "bottomLeft",
                    "bottomRight",
                ]
            ],
            "template": NotRequired[str],
            "style": NotRequired[dict],
            "transform": NotRequired[str],
        },
    )

    def __init__(
        self,
        min: typing.Optional[NumberType] = None,
        max: typing.Optional[NumberType] = None,
        step: typing.Optional[NumberType] = None,
        marks: typing.Optional[
            typing.Dict[typing.Union[str, float, int], typing.Union[str, "Marks"]]
        ] = None,
        value: typing.Optional[NumberType] = None,
        drag_value: typing.Optional[NumberType] = None,
        disabled: typing.Optional[bool] = None,
        dots: typing.Optional[bool] = None,
        included: typing.Optional[bool] = None,
        tooltip: typing.Optional["Tooltip"] = None,
        updatemode: typing.Optional[Literal["mouseup", "drag"]] = None,
        vertical: typing.Optional[bool] = None,
        verticalHeight: typing.Optional[NumberType] = None,
        reverse: typing.Optional[bool] = None,
        className: typing.Optional[str] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        persistence: typing.Optional[typing.Union[bool, str, NumberType]] = None,
        persisted_props: typing.Optional[typing.Sequence[Literal["value"]]] = None,
        persistence_type: typing.Optional[Literal["local", "session", "memory"]] = None,
        **kwargs
    ):
        self._prop_names = [
            "min",
            "max",
            "step",
            "marks",
            "value",
            "drag_value",
            "disabled",
            "dots",
            "included",
            "tooltip",
            "updatemode",
            "vertical",
            "verticalHeight",
            "reverse",
            "className",
            "id",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "min",
            "max",
            "step",
            "marks",
            "value",
            "drag_value",
            "disabled",
            "dots",
            "included",
            "tooltip",
            "updatemode",
            "vertical",
            "verticalHeight",
            "reverse",
            "className",
            "id",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Slider, self).__init__(**args)


setattr(Slider, "__init__", _explicitize_args(Slider.__init__))
