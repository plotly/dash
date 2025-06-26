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


class Button(Component):
    """A Button component.
    Button is a wrapper for the <button> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button

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

    - autoFocus (a value equal to: 'autoFocus', 'autofocus', 'AUTOFOCUS' | boolean; optional):
        The element should be automatically focused after the page loaded.

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

    - disabled (a value equal to: 'disabled', 'DISABLED' | boolean; optional):
        Indicates whether the user can interact with the element.

    - draggable (string; optional):
        Defines whether the element can be dragged.

    - form (string; optional):
        Indicates the form that is the owner of the element.

    - formAction (string; optional):
        Indicates the action of the element, overriding the action defined
        in the <form>.

    - formEncType (string; optional):
        If the button/input is a submit button (e.g., type=\"submit\"),
        this attribute sets the encoding type to use during form
        submission. If this attribute is specified, it overrides the
        enctype attribute of the button's form owner.

    - formMethod (string; optional):
        If the button/input is a submit button (e.g., type=\"submit\"),
        this attribute sets the submission method to use during form
        submission (GET, POST, etc.). If this attribute is specified, it
        overrides the method attribute of the button's form owner.

    - formNoValidate (a value equal to: 'formNoValidate', 'formnovalidate', 'FORMNOVALIDATE' | boolean; optional):
        If the button/input is a submit button (e.g., type=\"submit\"),
        this boolean attribute specifies that the form is not to be
        validated when it is submitted. If this attribute is specified, it
        overrides the novalidate attribute of the button's form owner.

    - formTarget (string; optional):
        If the button/input is a submit button (e.g., type=\"submit\"),
        this attribute specifies the browsing context (for example, tab,
        window, or inline frame) in which to display the response that is
        received after submitting the form. If this attribute is
        specified, it overrides the target attribute of the button's form
        owner.

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

    - name (string; optional):
        Name of the element. For example used by the server to identify
        the fields in form submits.

    - role (string; optional):
        Defines an explicit role for an element for use by assistive
        technologies.

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - tabIndex (string | number; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element.

    - type (string; optional):
        Defines the type of the element.

    - value (string; optional):
        Defines a default value which will be displayed in the element on
        page load."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_html_components"
    _type = "Button"

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        n_clicks: typing.Optional[NumberType] = None,
        n_clicks_timestamp: typing.Optional[NumberType] = None,
        disable_n_clicks: typing.Optional[bool] = None,
        key: typing.Optional[str] = None,
        autoFocus: typing.Optional[
            typing.Union[Literal["autoFocus", "autofocus", "AUTOFOCUS"], bool]
        ] = None,
        disabled: typing.Optional[
            typing.Union[Literal["disabled", "DISABLED"], bool]
        ] = None,
        form: typing.Optional[str] = None,
        formAction: typing.Optional[str] = None,
        formEncType: typing.Optional[str] = None,
        formMethod: typing.Optional[str] = None,
        formNoValidate: typing.Optional[
            typing.Union[
                Literal["formNoValidate", "formnovalidate", "FORMNOVALIDATE"], bool
            ]
        ] = None,
        formTarget: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        type: typing.Optional[str] = None,
        value: typing.Optional[str] = None,
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
            "autoFocus",
            "className",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "disabled",
            "draggable",
            "form",
            "formAction",
            "formEncType",
            "formMethod",
            "formNoValidate",
            "formTarget",
            "hidden",
            "key",
            "lang",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
            "type",
            "value",
        ]
        self._valid_wildcard_attributes = ["data-", "aria-"]
        self.available_properties = [
            "children",
            "id",
            "accessKey",
            "aria-*",
            "autoFocus",
            "className",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "disabled",
            "draggable",
            "form",
            "formAction",
            "formEncType",
            "formMethod",
            "formNoValidate",
            "formTarget",
            "hidden",
            "key",
            "lang",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
            "type",
            "value",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Button, self).__init__(children=children, **args)


setattr(Button, "__init__", _explicitize_args(Button.__init__))
