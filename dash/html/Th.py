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


class Th(Component):
    """A Th component.
    Th is a wrapper for the <th> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The children of this component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - accessKey (string; optional):
        Keyboard shortcut to activate or add focus to the element.

    - aria-* (string; optional):
        A wildcard aria attribute.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

    - colSpan (string | number; optional):
        The colspan attribute defines the number of columns a cell should
        span.

    - contentEditable (string; optional):
        Indicates whether the element's content is editable.

    - data-* (string; optional):
        A wildcard data attribute.

    - dir (string; optional):
        Defines the text direction. Allowed values are ltr (Left-To-Right)
        or rtl (Right-To-Left).

    - disable_n_clicks (boolean; optional):
        When True, this will disable the n_clicks prop.  Use this to
        remove event listeners that may interfere with screen readers.

    - draggable (string; optional):
        Defines whether the element can be dragged.

    - headers (string; optional):
        IDs of the <th> elements which applies to this element.

    - hidden (a value equal to: 'hidden', 'HIDDEN' | boolean; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

    - key (string; optional):
        A unique identifier for the component, used to improve performance
        by React.js while rendering components See
        https://reactjs.org/docs/lists-and-keys.html for more info.

    - lang (string; optional):
        Defines the language used in the element.

    - n_clicks (number; default 0):
        An integer that represents the number of times that this element
        has been clicked on.

    - n_clicks_timestamp (number; default -1):
        An integer that represents the time (in ms since 1970) at which
        n_clicks changed. This can be used to tell which button was
        changed most recently.

    - role (string; optional):
        Defines an explicit role for an element for use by assistive
        technologies.

    - rowSpan (string | number; optional):
        Defines the number of rows a table cell should span over.

    - scope (string; optional):
        Defines the cells that the header test (defined in the th element)
        relates to.

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - tabIndex (string | number; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_html_components"
    _type = "Th"

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        n_clicks: typing.Optional[NumberType] = None,
        n_clicks_timestamp: typing.Optional[NumberType] = None,
        disable_n_clicks: typing.Optional[bool] = None,
        key: typing.Optional[str] = None,
        colSpan: typing.Optional[typing.Union[str, NumberType]] = None,
        headers: typing.Optional[str] = None,
        rowSpan: typing.Optional[typing.Union[str, NumberType]] = None,
        scope: typing.Optional[str] = None,
        accessKey: typing.Optional[str] = None,
        className: typing.Optional[str] = None,
        contentEditable: typing.Optional[str] = None,
        dir: typing.Optional[str] = None,
        draggable: typing.Optional[str] = None,
        hidden: typing.Optional[typing.Union[Literal["hidden", "HIDDEN"], bool]] = None,
        lang: typing.Optional[str] = None,
        role: typing.Optional[str] = None,
        spellCheck: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        tabIndex: typing.Optional[typing.Union[str, NumberType]] = None,
        title: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "accessKey",
            "aria-*",
            "className",
            "colSpan",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "headers",
            "hidden",
            "key",
            "lang",
            "n_clicks",
            "n_clicks_timestamp",
            "role",
            "rowSpan",
            "scope",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
        ]
        self._valid_wildcard_attributes = ["data-", "aria-"]
        self.available_properties = [
            "children",
            "id",
            "accessKey",
            "aria-*",
            "className",
            "colSpan",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "headers",
            "hidden",
            "key",
            "lang",
            "n_clicks",
            "n_clicks_timestamp",
            "role",
            "rowSpan",
            "scope",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Th, self).__init__(children=children, **args)


setattr(Th, "__init__", _explicitize_args(Th.__init__))
