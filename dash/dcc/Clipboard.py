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


class Clipboard(Component):
    """A Clipboard component.
    The Clipboard component copies text to the clipboard

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        Children rendered inside the Clipboard button before copying. By
        default, a copy icon.

    - id (string; optional):
        The ID used to identify this component.

    - className (string; optional):
        The class  name of the icon element.

    - content (string; optional):
        The text to be copied to the clipboard if the `target_id` is None.

    - copied_children (a list of or a singular dash component, string or number; optional):
        Children rendered inside the Clipboard button after the value has
        been copied. By default, a check icon.

    - html_content (string; optional):
        The clipboard html text be copied to the clipboard if the
        `target_id` is None.

    - n_clicks (number; default 0):
        The number of times Clipboard button was clicked.

    - target_id (string | dict; optional):
        The id of target component containing text to copy to the
        clipboard. The inner text of the `children` prop will be copied to
        the clipboard.  If none, then the text from the  `value` prop will
        be copied.

    - title (string; optional):
        The text shown as a tooltip when hovering over the copy icon."""

    _children_props: typing.List[str] = ["copied_children"]
    _base_nodes = ["copied_children", "children"]
    _namespace = "dash_core_components"
    _type = "Clipboard"

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        copied_children: typing.Optional[ComponentType] = None,
        target_id: typing.Optional[typing.Union[str, dict]] = None,
        content: typing.Optional[str] = None,
        n_clicks: typing.Optional[NumberType] = None,
        html_content: typing.Optional[str] = None,
        title: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        className: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "className",
            "content",
            "copied_children",
            "html_content",
            "n_clicks",
            "style",
            "target_id",
            "title",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "className",
            "content",
            "copied_children",
            "html_content",
            "n_clicks",
            "style",
            "target_id",
            "title",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Clipboard, self).__init__(children=children, **args)


setattr(Clipboard, "__init__", _explicitize_args(Clipboard.__init__))
