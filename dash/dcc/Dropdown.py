# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class Dropdown(Component):
    """A Dropdown component.
    Dropdown is an interactive dropdown element for selecting one or more
    items.
    The values and labels of the dropdown items are specified in the `options`
    property and the selected item(s) are specified with the `value` property.
    *
    Use a dropdown when you have many options (more than 5) or when you are
    constrained for space. Otherwise, you can use RadioItems or a Checklist,
    which have the benefit of showing the users all of the items at once.

    Keyword arguments:

    - options (boolean | number | string | dict | list; optional):
        An array of options {label: [string|number], value:
        [string|number]}, an optional disabled field can be used for each
        option.

    - value (string | number | boolean | list of string | number | booleans; optional):
        The value of the input. If `multi` is False (the default) then
        value is just a string that corresponds to the values provided in
        the `options` property. If `multi` is True, then multiple values
        can be selected at once, and `value` is an array of items with
        values corresponding to those in the `options` prop.

    - multi (boolean; default False):
        If True, the user can select multiple values.

    - clearable (boolean; default True):
        Whether or not the dropdown is \"clearable\", that is, whether or
        not a small \"x\" appears on the right of the dropdown that
        removes the selected value.

    - searchable (boolean; default True):
        Whether to enable the searching feature or not.

    - search_value (string; optional):
        The value typed in the DropDown for searching.

    - placeholder (string; optional):
        The grey, default text shown when no option is selected.

    - disabled (boolean; default False):
        If True, this dropdown is disabled and the selection cannot be
        changed.

    - closeOnSelect (boolean; default !multi):
        If False, the menu of the dropdown will not close once a value is
        selected.

    - optionHeight (number; default 'auto'):
        height of each option. Can be increased when label lengths would
        wrap around.

    - maxHeight (number; default 200):
        height of the options dropdown.

    - labels (dict; default defaultLabels):
        Text for customizing the labels rendered by this component.

        `labels` is a dict with keys:

        - select_all (string; optional)

        - deselect_all (string; optional)

        - selected_count (string; optional)

        - search (string; optional)

        - clear_search (string; optional)

        - clear_selection (string; optional)

        - no_options_found (string; optional)

    - debounce (boolean; optional):
        If True, changes to input values will be sent back to the Dash
        server only when dropdown menu closes. Use with
        `closeOnSelect=False`.

    - className (string; optional):
        Additional CSS class for the root DOM node.

    - persistence (string | number | boolean; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (boolean | number | string | dict | list; default [PersistedProps.value]):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: None, 'local', 'session', 'memory'; default PersistenceTypes.local):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - componentPath (boolean | number | string | dict | list; optional)"""

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Dropdown"
    Labels = TypedDict(
        "Labels",
        {
            "select_all": NotRequired[typing.Union[str]],
            "deselect_all": NotRequired[typing.Union[str]],
            "selected_count": NotRequired[typing.Union[str]],
            "search": NotRequired[typing.Union[str]],
            "clear_search": NotRequired[typing.Union[str]],
            "clear_selection": NotRequired[typing.Union[str]],
            "no_options_found": NotRequired[typing.Union[str]],
        },
    )

    def __init__(
        self,
        options: typing.Optional[typing.Any] = None,
        value: typing.Optional[
            typing.Union[
                str,
                NumberType,
                bool,
                typing.Sequence[typing.Union[str, NumberType, bool]],
            ]
        ] = None,
        multi: typing.Optional[typing.Union[bool]] = None,
        clearable: typing.Optional[typing.Union[bool]] = None,
        searchable: typing.Optional[typing.Union[bool]] = None,
        search_value: typing.Optional[typing.Union[str]] = None,
        placeholder: typing.Optional[typing.Union[str]] = None,
        disabled: typing.Optional[typing.Union[bool]] = None,
        closeOnSelect: typing.Optional[typing.Union[bool]] = None,
        optionHeight: typing.Optional[typing.Union[NumberType, Literal["auto"]]] = None,
        maxHeight: typing.Optional[typing.Union[NumberType]] = None,
        style: typing.Optional[typing.Any] = None,
        labels: typing.Optional[typing.Union["Labels"]] = None,
        debounce: typing.Optional[typing.Union[bool]] = None,
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
            "options",
            "value",
            "multi",
            "clearable",
            "searchable",
            "search_value",
            "placeholder",
            "disabled",
            "closeOnSelect",
            "optionHeight",
            "maxHeight",
            "style",
            "labels",
            "debounce",
            "className",
            "persistence",
            "persisted_props",
            "persistence_type",
            "id",
            "componentPath",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "options",
            "value",
            "multi",
            "clearable",
            "searchable",
            "search_value",
            "placeholder",
            "disabled",
            "closeOnSelect",
            "optionHeight",
            "maxHeight",
            "style",
            "labels",
            "debounce",
            "className",
            "persistence",
            "persisted_props",
            "persistence_type",
            "id",
            "componentPath",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Dropdown, self).__init__(**args)


setattr(Dropdown, "__init__", _explicitize_args(Dropdown.__init__))
