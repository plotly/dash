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


class Form(Component):
    """A Form component.
    Form is a wrapper for the <form> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The children of this component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - accept (string; optional):
        List of types the server accepts, typically a file type.

    - acceptCharset (string; optional):
        The character set, which if provided must be \"UTF-8\".

    - accessKey (string; optional):
        Keyboard shortcut to activate or add focus to the element.

    - action (string; optional):
        The URI of a program that processes the information submitted via
        the form.

    - aria-* (string; optional):
        A wildcard aria attribute.

    - autoComplete (string; optional):
        Indicates whether controls in this form can by default have their
        values automatically completed by the browser.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

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

    - encType (string; optional):
        Defines the content type of the form data when the method is POST.

    - hidden (a value equal to: 'hidden', 'HIDDEN' | boolean; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

    - key (string; optional):
        A unique identifier for the component, used to improve performance
        by React.js while rendering components See
        https://reactjs.org/docs/lists-and-keys.html for more info.

    - lang (string; optional):
        Defines the language used in the element.

    - method (string; optional):
        Defines which HTTP method to use when submitting the form. Can be
        GET (default) or POST.

    - n_clicks (number; default 0):
        An integer that represents the number of times that this element
        has been clicked on.

    - n_clicks_timestamp (number; default -1):
        An integer that represents the time (in ms since 1970) at which
        n_clicks changed. This can be used to tell which button was
        changed most recently.

    - name (string; optional):
        Name of the element. For example used by the server to identify
        the fields in form submits.

    - noValidate (a value equal to: 'noValidate', 'novalidate', 'NOVALIDATE' | boolean; optional):
        This attribute indicates that the form shouldn't be validated when
        submitted.

    - role (string; optional):
        Defines an explicit role for an element for use by assistive
        technologies.

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - tabIndex (string | number; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - target (string; optional):
        Specifies where to open the linked document (in the case of an <a>
        element) or where to display the response received (in the case of
        a <form> element).

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element."""

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_html_components"
    _type = "Form"

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        n_clicks: typing.Optional[NumberType] = None,
        n_clicks_timestamp: typing.Optional[NumberType] = None,
        disable_n_clicks: typing.Optional[bool] = None,
        key: typing.Optional[str] = None,
        accept: typing.Optional[str] = None,
        acceptCharset: typing.Optional[str] = None,
        action: typing.Optional[str] = None,
        autoComplete: typing.Optional[str] = None,
        encType: typing.Optional[str] = None,
        method: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        noValidate: typing.Optional[
            typing.Union[Literal["noValidate", "novalidate", "NOVALIDATE"], bool]
        ] = None,
        target: typing.Optional[str] = None,
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
            "accept",
            "acceptCharset",
            "accessKey",
            "action",
            "aria-*",
            "autoComplete",
            "className",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "encType",
            "hidden",
            "key",
            "lang",
            "method",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "noValidate",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "target",
            "title",
        ]
        self._valid_wildcard_attributes = ["data-", "aria-"]
        self.available_properties = [
            "children",
            "id",
            "accept",
            "acceptCharset",
            "accessKey",
            "action",
            "aria-*",
            "autoComplete",
            "className",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "encType",
            "hidden",
            "key",
            "lang",
            "method",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "noValidate",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "target",
            "title",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Form, self).__init__(children=children, **args)


setattr(Form, "__init__", _explicitize_args(Form.__init__))
