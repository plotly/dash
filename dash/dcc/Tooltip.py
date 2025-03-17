# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


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

    - background_color (string; default 'white'):
        Color of the tooltip background, as a CSS color string.

    - bbox (dict; optional):
        The bounding box coordinates of the item to label, in px relative
        to the positioning parent of the Tooltip component.

        `bbox` is a dict with keys:

        - x0 (number; optional)

        - y0 (number; optional)

        - x1 (number; optional)

        - y1 (number; optional)

    - border_color (string; default '#d6d6d6'):
        Color of the tooltip border, as a CSS color string.

    - className (string; default ''):
        The class of the tooltip.

    - direction (a value equal to: 'top', 'right', 'bottom', 'left'; default 'right'):
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

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Tooltip"
    Bbox = TypedDict(
        "Bbox",
        {
            "x0": NotRequired[typing.Union[int, float, numbers.Number]],
            "y0": NotRequired[typing.Union[int, float, numbers.Number]],
            "x1": NotRequired[typing.Union[int, float, numbers.Number]],
            "y1": NotRequired[typing.Union[int, float, numbers.Number]],
        },
    )

    @_explicitize_args
    def __init__(
        self,
        children: typing.Optional[
            typing.Union[
                str,
                int,
                float,
                ComponentType,
                typing.Sequence[typing.Union[str, int, float, ComponentType]],
            ]
        ] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        className: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        bbox: typing.Optional["Bbox"] = None,
        show: typing.Optional[bool] = None,
        direction: typing.Optional[Literal["top", "right", "bottom", "left"]] = None,
        border_color: typing.Optional[str] = None,
        background_color: typing.Optional[str] = None,
        loading_text: typing.Optional[str] = None,
        zindex: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        targetable: typing.Optional[bool] = None,
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
