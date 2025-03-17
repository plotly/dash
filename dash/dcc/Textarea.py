# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Textarea(Component):
    """A Textarea component.
    A basic HTML textarea for entering multiline text.

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
        Often used with CSS to style elements with common properties.

    - cols (string | number; optional):
        Defines the number of columns in a textarea.

    - contentEditable (string | boolean; optional):
        Indicates whether the element's content is editable.

    - contextMenu (string; optional):
        Defines the ID of a <menu> element which will serve as the
        element's context menu.

    - dir (string; optional):
        Defines the text direction. Allowed values are ltr (Left-To-Right)
        or rtl (Right-To-Left).

    - disabled (string | boolean; optional):
        Indicates whether the user can interact with the element.

    - draggable (a value equal to: 'true', 'false' | boolean; optional):
        Defines whether the element can be dragged.

    - form (string; optional):
        Indicates the form that is the owner of the element.

    - hidden (string; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

    - lang (string; optional):
        Defines the language used in the element.

    - maxLength (string | number; optional):
        Defines the maximum number of characters allowed in the element.

    - minLength (string | number; optional):
        Defines the minimum number of characters allowed in the element.

    - n_blur (number; default 0):
        Number of times the textarea lost focus.

    - n_blur_timestamp (number; default -1):
        Last time the textarea lost focus.

    - n_clicks (number; optional):
        Number of times the textarea has been clicked.

    - n_clicks_timestamp (number; default -1):
        Last time the textarea was clicked.

    - name (string; optional):
        Name of the element. For example used by the server to identify
        the fields in form submits.

    - persisted_props (list of a value equal to: 'value's; optional):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence (boolean | string | number; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persistence_type (a value equal to: 'local', 'session', 'memory'; optional):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit.

    - placeholder (string; optional):
        Provides a hint to the user of what can be entered in the field.

    - readOnly (boolean | a value equal to: 'readOnly', 'readonly', 'READONLY'; optional):
        Indicates whether the element can be edited. readOnly is an HTML
        boolean attribute - it is enabled by a boolean or 'readOnly'.
        Alternative capitalizations `readonly` & `READONLY` are also
        acccepted.

    - required (a value equal to: 'required', 'REQUIRED' | boolean; optional):
        Indicates whether this element is required to fill out or not.
        required is an HTML boolean attribute - it is enabled by a boolean
        or 'required'. Alternative capitalizations `REQUIRED` are also
        acccepted.

    - rows (string | number; optional):
        Defines the number of rows in a text area.

    - spellCheck (a value equal to: 'true', 'false' | boolean; optional):
        Indicates whether spell checking is allowed for the element.

    - tabIndex (string | number; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element.

    - value (string; optional):
        The value of the textarea.

    - wrap (string; optional):
        Indicates whether the text should be wrapped."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Textarea"

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        value: typing.Optional[str] = None,
        autoFocus: typing.Optional[str] = None,
        cols: typing.Optional[
            typing.Union[str, typing.Union[int, float, numbers.Number]]
        ] = None,
        disabled: typing.Optional[typing.Union[str, bool]] = None,
        form: typing.Optional[str] = None,
        maxLength: typing.Optional[
            typing.Union[str, typing.Union[int, float, numbers.Number]]
        ] = None,
        minLength: typing.Optional[
            typing.Union[str, typing.Union[int, float, numbers.Number]]
        ] = None,
        name: typing.Optional[str] = None,
        placeholder: typing.Optional[str] = None,
        readOnly: typing.Optional[
            typing.Union[bool, Literal["readOnly", "readonly", "READONLY"]]
        ] = None,
        required: typing.Optional[
            typing.Union[Literal["required", "REQUIRED"], bool]
        ] = None,
        rows: typing.Optional[
            typing.Union[str, typing.Union[int, float, numbers.Number]]
        ] = None,
        wrap: typing.Optional[str] = None,
        accessKey: typing.Optional[str] = None,
        className: typing.Optional[str] = None,
        contentEditable: typing.Optional[typing.Union[str, bool]] = None,
        contextMenu: typing.Optional[str] = None,
        dir: typing.Optional[str] = None,
        draggable: typing.Optional[typing.Union[Literal["true", "false"], bool]] = None,
        hidden: typing.Optional[str] = None,
        lang: typing.Optional[str] = None,
        spellCheck: typing.Optional[
            typing.Union[Literal["true", "false"], bool]
        ] = None,
        style: typing.Optional[typing.Any] = None,
        tabIndex: typing.Optional[
            typing.Union[str, typing.Union[int, float, numbers.Number]]
        ] = None,
        title: typing.Optional[str] = None,
        n_blur: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        n_blur_timestamp: typing.Optional[
            typing.Union[int, float, numbers.Number]
        ] = None,
        n_clicks: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        n_clicks_timestamp: typing.Optional[
            typing.Union[int, float, numbers.Number]
        ] = None,
        persistence: typing.Optional[
            typing.Union[bool, str, typing.Union[int, float, numbers.Number]]
        ] = None,
        persisted_props: typing.Optional[typing.Sequence[Literal["value"]]] = None,
        persistence_type: typing.Optional[Literal["local", "session", "memory"]] = None,
        **kwargs
    ):
        self._prop_names = [
            "id",
            "accessKey",
            "autoFocus",
            "className",
            "cols",
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
