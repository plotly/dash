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


class Button(Component):
    """A Button component.
    Similar to dash.html.Button, but with theming and styles applied.

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The children of this component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - accessKey (string; optional):
        Keyboard shortcut to activate or add focus to the element.

    - autoFocus (boolean; optional):
        The element should be automatically focused after the page loaded.

    - className (string; optional):
        Additional CSS class for the root DOM node.

    - componentPath (boolean | number | string | dict | list; optional)

    - contentEditable (boolean; optional):
        Indicates whether the element's content is editable.

    - dir (string; optional):
        Defines the text direction. Allowed values are ltr (Left-To-Right)
        or rtl (Right-To-Left).

    - disabled (boolean; optional):
        Indicates whether the user can interact with the element.

    - draggable (boolean; optional):
        Defines whether the element can be dragged.

    - form (string; optional):
        Indicates the form that is the owner of the element.

    - formAction (string; optional):
        Indicates the action of the element, overriding the action defined
        in the <form>.

    - formEncType (string; optional):
        If the button/input is a submit button (type=\"submit\"), this
        attribute sets the encoding type to use during form submission. If
        this attribute is specified, it overrides the enctype attribute of
        the button's form owner.

    - formMethod (string; optional):
        If the button/input is a submit button (type=\"submit\"), this
        attribute sets the submission method to use during form submission
        (GET, POST, etc.). If this attribute is specified, it overrides
        the method attribute of the button's form owner.

    - formNoValidate (boolean; optional):
        If the button/input is a submit button (type=\"submit\"), this
        boolean attribute specifies that the form is not to be validated
        when it is submitted. If this attribute is specified, it overrides
        the novalidate attribute of the button's form owner.

    - formTarget (string; optional):
        If the button/input is a submit button (type=\"submit\"), this
        attribute specifies the browsing context (for example, tab,
        window, or inline frame) in which to display the response that is
        received after submitting the form. If this attribute is
        specified, it overrides the target attribute of the button's form
        owner.

    - hidden (boolean; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

    - lang (string; optional):
        Defines the language used in the element.

    - n_blur (number; default 0):
        Number of times the button lost focus.

    - n_blur_timestamp (number; default -1):
        Last time the button lost focus.

    - n_clicks (number; default 0):
        Number of times the button has been clicked.

    - n_clicks_timestamp (number; default -1):
        Last time the button was clicked.

    - name (string; optional):
        Name of the element. For example used by the server to identify
        the fields in form submits.

    - persisted_props (boolean | number | string | dict | list; optional):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence (string | number | boolean; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persistence_type (a value equal to: None, 'local', 'session', 'memory'; optional):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit.

    - role (string; optional):
        Defines the role of an element in the context of accessibility.

    - spellCheck (boolean; optional):
        Indicates whether spell checking is allowed for the element.

    - tabIndex (number; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element.

    - type (a value equal to: None, 'submit', 'reset', 'button'; default 'button'):
        Defines the type of the element.

    - value (string | number | list of strings; optional):
        Defines a default value which will be displayed in the element on
        page load."""

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Button"

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        className: typing.Optional[typing.Union[str]] = None,
        persistence: typing.Optional[typing.Union[str, NumberType, bool]] = None,
        persisted_props: typing.Optional[typing.Any] = None,
        persistence_type: typing.Optional[
            Literal[None, "local", "session", "memory"]
        ] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        componentPath: typing.Optional[typing.Any] = None,
        type: typing.Optional[Literal[None, "submit", "reset", "button"]] = None,
        autoFocus: typing.Optional[typing.Union[bool]] = None,
        disabled: typing.Optional[typing.Union[bool]] = None,
        form: typing.Optional[typing.Union[str]] = None,
        formAction: typing.Optional[typing.Union[str]] = None,
        formEncType: typing.Optional[typing.Union[str]] = None,
        formMethod: typing.Optional[typing.Union[str]] = None,
        formNoValidate: typing.Optional[typing.Union[bool]] = None,
        formTarget: typing.Optional[typing.Union[str]] = None,
        name: typing.Optional[typing.Union[str]] = None,
        value: typing.Optional[
            typing.Union[str, NumberType, typing.Sequence[str]]
        ] = None,
        accessKey: typing.Optional[typing.Union[str]] = None,
        contentEditable: typing.Optional[
            typing.Union[bool, Literal["true"], Literal["false"], Literal["inherit"]]
        ] = None,
        dir: typing.Optional[typing.Union[str]] = None,
        draggable: typing.Optional[typing.Union[bool]] = None,
        hidden: typing.Optional[typing.Union[bool]] = None,
        lang: typing.Optional[typing.Union[str]] = None,
        role: typing.Optional[typing.Union[str]] = None,
        spellCheck: typing.Optional[typing.Union[bool]] = None,
        style: typing.Optional[typing.Any] = None,
        tabIndex: typing.Optional[typing.Union[NumberType]] = None,
        title: typing.Optional[typing.Union[str]] = None,
        n_blur: typing.Optional[typing.Union[NumberType]] = None,
        n_blur_timestamp: typing.Optional[typing.Union[NumberType]] = None,
        n_clicks: typing.Optional[typing.Union[NumberType]] = None,
        n_clicks_timestamp: typing.Optional[typing.Union[NumberType]] = None,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "accessKey",
            "autoFocus",
            "className",
            "componentPath",
            "contentEditable",
            "dir",
            "disabled",
            "draggable",
            "form",
            "formAction",
            "formEncType",
            "formMethod",
            "formNoValidate",
            "formTarget",
            "hidden",
            "lang",
            "n_blur",
            "n_blur_timestamp",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "persisted_props",
            "persistence",
            "persistence_type",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
            "type",
            "value",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "accessKey",
            "autoFocus",
            "className",
            "componentPath",
            "contentEditable",
            "dir",
            "disabled",
            "draggable",
            "form",
            "formAction",
            "formEncType",
            "formMethod",
            "formNoValidate",
            "formTarget",
            "hidden",
            "lang",
            "n_blur",
            "n_blur_timestamp",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "persisted_props",
            "persistence",
            "persistence_type",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
            "type",
            "value",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Button, self).__init__(children=children, **args)


setattr(Button, "__init__", _explicitize_args(Button.__init__))
