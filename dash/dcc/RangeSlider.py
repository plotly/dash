# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

try:
    from dash.types import NumberType  # noqa: F401
except ImportError:
    # Backwards compatibility for dash<=4.1.0
    if typing.TYPE_CHECKING:
        raise
    NumberType = typing.Union[  # noqa: F401
        typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
    ]

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]


class RangeSlider(Component):
    """A RangeSlider component.
    A double slider with two handles.
    Used for specifying a range of numerical values.

    Keyword arguments:

    - min (number; optional):
        Minimum allowed value of the slider.

    - max (number; optional):
        Maximum allowed value of the slider.

    - step (number; default undefined):
        Value by which increments or decrements are made.

    - marks (boolean | number | string | dict | list; optional):
        Marks on the slider. The key determines the position (a number),
        and the value determines what will show. If you want to set the
        style of a specific mark point, the value should be an object
        which contains style and label properties.

    - value (list of numbers; optional):
        The value of the input.

    - drag_value (list of numbers; optional):
        The value of the input during a drag.

    - allowCross (boolean; optional):
        allowCross could be set as True to allow those handles to cross.

    - pushable (number | boolean; optional):
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

    - reverse (boolean; optional):
        If the value is True, the slider is rendered in reverse.

    - tooltip (boolean | number | string | dict | list; optional):
        Configuration for tooltips describing the current slider values.

    - updatemode (a value equal to: None, 'mouseup', 'drag'; default 'mouseup'):
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

    - allow_direct_input (boolean; default True):
        If False, the input elements for directly entering values will be
        hidden. Only the slider will be visible and it will occupy 100%
        width of the container.

    - className (string; optional):
        Additional CSS class for the root DOM node.

    - persistence (string | number | boolean; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (boolean | number | string | dict | list; default [PersistedProps.value]):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: None, 'local', 'session', 'memory'; default PersistenceTypes.local):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - componentPath (boolean | number | string | dict | list; optional)"""

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "RangeSlider"

    def __init__(
        self,
        min: typing.Optional[typing.Union[NumberType]] = None,
        max: typing.Optional[typing.Union[NumberType]] = None,
        step: typing.Optional[typing.Union[NumberType]] = None,
        marks: typing.Optional[typing.Any] = None,
        value: typing.Optional[typing.Union[typing.Sequence[NumberType]]] = None,
        drag_value: typing.Optional[typing.Union[typing.Sequence[NumberType]]] = None,
        allowCross: typing.Optional[typing.Union[bool]] = None,
        pushable: typing.Optional[typing.Union[NumberType, bool]] = None,
        disabled: typing.Optional[typing.Union[bool]] = None,
        count: typing.Optional[typing.Union[NumberType]] = None,
        dots: typing.Optional[typing.Union[bool]] = None,
        included: typing.Optional[typing.Union[bool]] = None,
        reverse: typing.Optional[typing.Union[bool]] = None,
        tooltip: typing.Optional[typing.Any] = None,
        updatemode: typing.Optional[Literal[None, "mouseup", "drag"]] = None,
        vertical: typing.Optional[typing.Union[bool]] = None,
        verticalHeight: typing.Optional[typing.Union[NumberType]] = None,
        allow_direct_input: typing.Optional[typing.Union[bool]] = None,
        className: typing.Optional[typing.Union[str]] = None,
        persistence: typing.Optional[typing.Union[str, NumberType, bool]] = None,
        persisted_props: typing.Optional[typing.Any] = None,
        persistence_type: typing.Optional[
            Literal[None, "local", "session", "memory"]
        ] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        componentPath: typing.Optional[typing.Any] = None,
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
            "reverse",
            "tooltip",
            "updatemode",
            "vertical",
            "verticalHeight",
            "allow_direct_input",
            "className",
            "persistence",
            "persisted_props",
            "persistence_type",
            "id",
            "componentPath",
        ]
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
            "reverse",
            "tooltip",
            "updatemode",
            "vertical",
            "verticalHeight",
            "allow_direct_input",
            "className",
            "persistence",
            "persisted_props",
            "persistence_type",
            "id",
            "componentPath",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(RangeSlider, self).__init__(**args)


setattr(RangeSlider, "__init__", _explicitize_args(RangeSlider.__init__))
