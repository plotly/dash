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


class Tooltip(Component):
    """A Tooltip component.
    A tooltip with an absolute position.

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The contents of the tooltip.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - background_color (string; default 'var(--Dash-Fill-Inverse-Strong)'):
        Color of the tooltip background, as a CSS color string.

    - bbox (dict; optional):
        The bounding box coordinates of the item to label, in px relative
        to the positioning parent of the Tooltip component.

        `bbox` is a dict with keys:

        - x0 (number; required)

        - y0 (number; required)

        - x1 (number; required)

        - y1 (number; required)

    - border_color (string; default 'var(--Dash-Stroke-Weak)'):
        Color of the tooltip border, as a CSS color string.

    - className (string; default ''):
        The class of the tooltip.

    - direction (a value equal to: None, 'top', 'right', 'bottom', 'left'; default 'right'):
        The side of the `bbox` on which the tooltip should open.

    - loading_text (string; default 'Loading...'):
        The text displayed in the tooltip while loading.

    - show (boolean; default True):
        Whether to show the tooltip.

    - targetable (boolean; default False):
        Whether the tooltip itself can be targeted by pointer events. For
        tooltips triggered by hover events, typically this should be left
        `False` to avoid the tooltip interfering with those same events.

    - zindex (number; default 1):
        The `z-index` CSS property to assign to the tooltip. Components
        with higher values will be displayed on top of components with
        lower values."""

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Tooltip"
    Bbox = TypedDict(
        "Bbox", {"x0": NumberType, "y0": NumberType, "x1": NumberType, "y1": NumberType}
    )

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        className: typing.Optional[typing.Union[str]] = None,
        style: typing.Optional[typing.Any] = None,
        bbox: typing.Optional[typing.Union["Bbox"]] = None,
        show: typing.Optional[typing.Union[bool]] = None,
        direction: typing.Optional[
            Literal[None, "top", "right", "bottom", "left"]
        ] = None,
        border_color: typing.Optional[typing.Union[str]] = None,
        background_color: typing.Optional[typing.Union[str]] = None,
        loading_text: typing.Optional[typing.Union[str]] = None,
        zindex: typing.Optional[typing.Union[NumberType]] = None,
        targetable: typing.Optional[typing.Union[bool]] = None,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "background_color",
            "bbox",
            "border_color",
            "className",
            "direction",
            "loading_text",
            "show",
            "style",
            "targetable",
            "zindex",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "background_color",
            "bbox",
            "border_color",
            "className",
            "direction",
            "loading_text",
            "show",
            "style",
            "targetable",
            "zindex",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Tooltip, self).__init__(children=children, **args)


setattr(Tooltip, "__init__", _explicitize_args(Tooltip.__init__))
