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


class Tab(Component):
    """A Tab component.


    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The content of the tab - will only be displayed if this tab is
        selected.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - className (string; optional):
        Appends a class to the Tab component.

    - componentPath (boolean | number | string | dict | list; optional)

    - disabled (boolean; default False):
        Determines if tab is disabled or not - defaults to False.

    - disabled_className (string; optional):
        Appends a class to the Tab component when it is disabled.

    - disabled_style (boolean | number | string | dict | list; default {color: 'var(--Dash-Text-Disabled)'}):
        Overrides the default (inline) styles when disabled.

    - label (string | a list of or a singular dash component, string or number; optional):
        The tab's label.

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

    - selected_className (string; optional):
        Appends a class to the Tab component when it is selected.

    - selected_style (boolean | number | string | dict | list; optional):
        Overrides the default (inline) styles for the Tab component when
        it is selected.

    - value (string; optional):
        Value for determining which Tab is currently selected.

    - width (string | number; optional):
        A custom width for this tab, in the format of `50px` or `50%`;
        numbers are treated as pixel values. By default, there is no width
        and this Tab is evenly spaced along with all the other tabs to
        occupy the available space. Setting this value will \"fix\" this
        tab width to the given size. while the other \"non-fixed\" tabs
        will continue to automatically occupying the remaining available
        space. This property has no effect when tabs are displayed
        vertically."""

    _children_props: typing.List[str] = ["label"]
    _base_nodes = ["label", "children"]
    _namespace = "dash_core_components"
    _type = "Tab"

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        label: typing.Optional[typing.Union[str, ComponentType]] = None,
        value: typing.Optional[typing.Union[str]] = None,
        disabled: typing.Optional[typing.Union[bool]] = None,
        disabled_style: typing.Optional[typing.Any] = None,
        disabled_className: typing.Optional[typing.Union[str]] = None,
        className: typing.Optional[typing.Union[str]] = None,
        selected_className: typing.Optional[typing.Union[str]] = None,
        style: typing.Optional[typing.Any] = None,
        selected_style: typing.Optional[typing.Any] = None,
        width: typing.Optional[typing.Union[str, NumberType]] = None,
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
            "children",
            "id",
            "className",
            "componentPath",
            "disabled",
            "disabled_className",
            "disabled_style",
            "label",
            "persisted_props",
            "persistence",
            "persistence_type",
            "selected_className",
            "selected_style",
            "style",
            "value",
            "width",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "className",
            "componentPath",
            "disabled",
            "disabled_className",
            "disabled_style",
            "label",
            "persisted_props",
            "persistence",
            "persistence_type",
            "selected_className",
            "selected_style",
            "style",
            "value",
            "width",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Tab, self).__init__(children=children, **args)


setattr(Tab, "__init__", _explicitize_args(Tab.__init__))
