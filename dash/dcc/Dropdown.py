# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Dropdown(Component):
    """A Dropdown component.
    Dropdown is an interactive dropdown element for selecting one or more
    items.
    The values and labels of the dropdown items are specified in the `options`
    property and the selected item(s) are specified with the `value` property.

    Use a dropdown when you have many options (more than 5) or when you are
    constrained for space. Otherwise, you can use RadioItems or a Checklist,
    which have the benefit of showing the users all of the items at once.

    Keyword arguments:

    - options (list of dicts; optional):
        An array of options {label: [string|number], value:
        [string|number]}, an optional disabled field can be used for each
        option.

        `options` is a list of string | number | booleans | dict | list of
        dicts with keys:

        - label (a list of or a singular dash component, string or number; required):
            The option's label.

        - value (string | number | boolean; required):
            The value of the option. This value corresponds to the items
            specified in the `value` property.

        - disabled (boolean; optional):
            If True, this option is disabled and cannot be selected.

        - title (string; optional):
            The HTML 'title' attribute for the option. Allows for
            information on hover. For more information on this attribute,
            see
            https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title.

        - search (string; optional):
            Optional search value for the option, to use if the label is a
            component or provide a custom search value different from the
            label. If no search value and the label is a component, the
            `value` will be used for search.

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

    - optionHeight (number; default 35):
        height of each option. Can be increased when label lengths would
        wrap around.

    - maxHeight (number; default 200):
        height of the options dropdown.

    - className (string; optional):
        className of the dropdown element.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - persistence (boolean | string | number; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (list of a value equal to: 'value's; default ['value']):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit."""

    _children_props = ["options[].label"]
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Dropdown"
    Options = TypedDict(
        "Options",
        {
            "label": typing.Union[
                str,
                int,
                float,
                ComponentType,
                typing.Sequence[typing.Union[str, int, float, ComponentType]],
            ],
            "value": typing.Union[str, typing.Union[int, float, numbers.Number], bool],
            "disabled": NotRequired[bool],
            "title": NotRequired[str],
            "search": NotRequired[str],
        },
    )

    @_explicitize_args
    def __init__(
        self,
        options: typing.Optional[
            typing.Union[
                typing.Sequence[
                    typing.Union[str, typing.Union[int, float, numbers.Number], bool]
                ],
                dict,
                typing.Sequence["Options"],
            ]
        ] = None,
        value: typing.Optional[
            typing.Union[
                str,
                typing.Union[int, float, numbers.Number],
                bool,
                typing.Sequence[
                    typing.Union[str, typing.Union[int, float, numbers.Number], bool]
                ],
            ]
        ] = None,
        multi: typing.Optional[bool] = None,
        clearable: typing.Optional[bool] = None,
        searchable: typing.Optional[bool] = None,
        search_value: typing.Optional[str] = None,
        placeholder: typing.Optional[str] = None,
        disabled: typing.Optional[bool] = None,
        optionHeight: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        maxHeight: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        style: typing.Optional[typing.Any] = None,
        className: typing.Optional[str] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        persistence: typing.Optional[
            typing.Union[bool, str, typing.Union[int, float, numbers.Number]]
        ] = None,
        persisted_props: typing.Optional[typing.Sequence[Literal["value"]]] = None,
        persistence_type: typing.Optional[Literal["local", "session", "memory"]] = None,
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
            "optionHeight",
            "maxHeight",
            "style",
            "className",
            "id",
            "persistence",
            "persisted_props",
            "persistence_type",
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
            "optionHeight",
            "maxHeight",
            "style",
            "className",
            "id",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Dropdown, self).__init__(**args)
