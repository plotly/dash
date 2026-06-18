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


class Textarea(Component):
    """A Textarea component.
    A basic HTML textarea for entering multiline text.
    *

    Keyword arguments:

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - accessKey (string; optional):
        Defines a keyboard shortcut to activate or add focus to the
        element.

    - autoFocus (string; optional):
        The element should be automatically focused after the page loaded.

    - className (string; optional):
        Additional CSS class for the root DOM node.

    - cols (number; optional):
        Defines the number of columns in a textarea.

    - componentPath (boolean | number | string | dict | list; optional)

    - contentEditable (boolean; optional):
        Indicates whether the element's content is editable.

    - contextMenu (string; optional):
        Defines the ID of a <menu> element which will serve as the
        element's context menu.

    - dir (string; optional):
        Defines the text direction. Allowed values are ltr (Left-To-Right)
        or rtl (Right-To-Left).

    - disabled (boolean; optional):
        Indicates whether the user can interact with the element.

    - draggable (boolean; optional):
        Defines whether the element can be dragged.

    - form (string; optional):
        Indicates the form that is the owner of the element.

    - hidden (string; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

    - lang (string; optional):
        Defines the language used in the element.

    - maxLength (number; optional):
        Defines the maximum number of characters allowed in the element.

    - minLength (number; optional):
        Defines the minimum number of characters allowed in the element.

    - n_blur (number; default 0):
        Number of times the textarea lost focus.

    - n_blur_timestamp (number; default -1):
        Last time the textarea lost focus.

    - n_clicks (number; default 0):
        Number of times the textarea has been clicked.

    - n_clicks_timestamp (number; default -1):
        Last time the textarea was clicked.

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

    - placeholder (string; optional):
        Provides a hint to the user of what can be entered in the field.

    - readOnly (boolean; optional):
        Indicates whether the element can be edited. readOnly is an HTML
        boolean attribute - it is enabled by a boolean or 'readOnly'.
        Alternative capitalizations `readonly` & `READONLY` are also
        acccepted.

    - required (boolean; optional):
        Indicates whether this element is required to fill out or not.
        required is an HTML boolean attribute - it is enabled by a boolean
        or 'required'. Alternative capitalizations `REQUIRED` are also
        acccepted.

    - rows (number; optional):
        Defines the number of rows in a text area.

    - spellCheck (boolean; optional):
        Indicates whether spell checking is allowed for the element.

    - tabIndex (number; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element.

    - value (string; optional):
        The value of the textarea.

    - wrap (string; optional):
        Indicates whether the text should be wrapped."""

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Textarea"

    def __init__(
        self,
        value: typing.Optional[typing.Union[str]] = None,
        autoFocus: typing.Optional[typing.Union[str]] = None,
        cols: typing.Optional[typing.Union[NumberType]] = None,
        disabled: typing.Optional[
            typing.Union[bool, Literal["disabled"], Literal["DISABLED"]]
        ] = None,
        form: typing.Optional[typing.Union[str]] = None,
        maxLength: typing.Optional[typing.Union[NumberType]] = None,
        minLength: typing.Optional[typing.Union[NumberType]] = None,
        name: typing.Optional[typing.Union[str]] = None,
        placeholder: typing.Optional[typing.Union[str]] = None,
        readOnly: typing.Optional[
            typing.Union[
                bool, Literal["readOnly"], Literal["readonly"], Literal["READONLY"]
            ]
        ] = None,
        required: typing.Optional[
            typing.Union[bool, Literal["required"], Literal["REQUIRED"]]
        ] = None,
        rows: typing.Optional[typing.Union[NumberType]] = None,
        wrap: typing.Optional[typing.Union[str]] = None,
        accessKey: typing.Optional[typing.Union[str]] = None,
        contentEditable: typing.Optional[typing.Union[bool]] = None,
        contextMenu: typing.Optional[typing.Union[str]] = None,
        dir: typing.Optional[typing.Union[str]] = None,
        draggable: typing.Optional[typing.Union[bool]] = None,
        hidden: typing.Optional[typing.Union[str]] = None,
        lang: typing.Optional[typing.Union[str]] = None,
        spellCheck: typing.Optional[typing.Union[bool]] = None,
        style: typing.Optional[typing.Any] = None,
        tabIndex: typing.Optional[typing.Union[NumberType]] = None,
        title: typing.Optional[typing.Union[str]] = None,
        n_blur: typing.Optional[typing.Union[NumberType]] = None,
        n_blur_timestamp: typing.Optional[typing.Union[NumberType]] = None,
        n_clicks: typing.Optional[typing.Union[NumberType]] = None,
        n_clicks_timestamp: typing.Optional[typing.Union[NumberType]] = None,
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
            "id",
            "accessKey",
            "autoFocus",
            "className",
            "cols",
            "componentPath",
            "contentEditable",
            "contextMenu",
            "dir",
            "disabled",
            "draggable",
            "form",
            "hidden",
            "lang",
            "maxLength",
            "minLength",
            "n_blur",
            "n_blur_timestamp",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "persisted_props",
            "persistence",
            "persistence_type",
            "placeholder",
            "readOnly",
            "required",
            "rows",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
            "value",
            "wrap",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "id",
            "accessKey",
            "autoFocus",
            "className",
            "cols",
            "componentPath",
            "contentEditable",
            "contextMenu",
            "dir",
            "disabled",
            "draggable",
            "form",
            "hidden",
            "lang",
            "maxLength",
            "minLength",
            "n_blur",
            "n_blur_timestamp",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "persisted_props",
            "persistence",
            "persistence_type",
            "placeholder",
            "readOnly",
            "required",
            "rows",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
            "value",
            "wrap",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Textarea, self).__init__(**args)


setattr(Textarea, "__init__", _explicitize_args(Textarea.__init__))
