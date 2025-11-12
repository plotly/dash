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


class Img(Component):
    """An Img component.
    Img is a wrapper for the <img> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The children of this component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - accessKey (string; optional):
        Keyboard shortcut to activate or add focus to the element.

    - alt (string; optional):
        Alternative text in case an image can't be displayed.

    - aria-* (string; optional):
        A wildcard aria attribute.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

    - contentEditable (string; optional):
        Indicates whether the element's content is editable.

    - crossOrigin (string; optional):
        How the element handles cross-origin requests.

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

    - height (string | number; optional):
        Specifies the height of elements listed here. For all other
        elements, use the CSS height property. Note: In some instances,
        such as <div>, this is a legacy attribute, in which case the CSS
        height property should be used instead.

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

    - referrerPolicy (string; optional):
        Specifies which referrer is sent when fetching the resource.

    - role (string; optional):
        Defines an explicit role for an element for use by assistive
        technologies.

    - sizes (string; optional)

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - src (string; optional):
        The URL of the embeddable content.

    - srcSet (string; optional):
        One or more responsive image candidates.

    - tabIndex (string | number; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element.

    - useMap (string; optional)

    - width (string | number; optional):
        For the elements listed here, this establishes the element's
        width. Note: For all other instances, such as <div>, this is a
        legacy attribute, in which case the CSS width property should be
        used instead."""

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_html_components"
    _type = "Img"

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        n_clicks: typing.Optional[NumberType] = None,
        n_clicks_timestamp: typing.Optional[NumberType] = None,
        disable_n_clicks: typing.Optional[bool] = None,
        key: typing.Optional[str] = None,
        alt: typing.Optional[str] = None,
        crossOrigin: typing.Optional[str] = None,
        height: typing.Optional[typing.Union[str, NumberType]] = None,
        referrerPolicy: typing.Optional[str] = None,
        sizes: typing.Optional[str] = None,
        src: typing.Optional[str] = None,
        srcSet: typing.Optional[str] = None,
        useMap: typing.Optional[str] = None,
        width: typing.Optional[typing.Union[str, NumberType]] = None,
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
            "alt",
            "aria-*",
            "className",
            "contentEditable",
            "crossOrigin",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "height",
            "hidden",
            "key",
            "lang",
            "n_clicks",
            "n_clicks_timestamp",
            "referrerPolicy",
            "role",
            "sizes",
            "spellCheck",
            "src",
            "srcSet",
            "style",
            "tabIndex",
            "title",
            "useMap",
            "width",
        ]
        self._valid_wildcard_attributes = ["data-", "aria-"]
        self.available_properties = [
            "children",
            "id",
            "accessKey",
            "alt",
            "aria-*",
            "className",
            "contentEditable",
            "crossOrigin",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "height",
            "hidden",
            "key",
            "lang",
            "n_clicks",
            "n_clicks_timestamp",
            "referrerPolicy",
            "role",
            "sizes",
            "spellCheck",
            "src",
            "srcSet",
            "style",
            "tabIndex",
            "title",
            "useMap",
            "width",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Img, self).__init__(children=children, **args)


setattr(Img, "__init__", _explicitize_args(Img.__init__))
