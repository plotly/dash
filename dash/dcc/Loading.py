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


class Loading(Component):
    """A Loading component.


    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        Array that holds components to render.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - className (string; optional):
        Additional CSS class for the root DOM node.

    - color (string; default 'var(--Dash-Fill-Interactive-Strong)'):
        Primary color used for the built-in loading spinners.

    - componentPath (boolean | number | string | dict | list; optional)

    - custom_spinner (a list of or a singular dash component, string or number; optional):
        Component to use rather than the built-in spinner specified in the
        `type` prop.

    - debug (boolean; optional):
        If True, the built-in spinner will display the component_name and
        prop_name while loading.

    - delay_hide (number; default 0):
        Add a time delay (in ms) to the spinner being removed to prevent
        flickering.

    - delay_show (number; default 0):
        Add a time delay (in ms) to the spinner being shown after the
        loading_state is set to True.

    - display (a value equal to: None, 'auto', 'show', 'hide'; default 'auto'):
        Setting display to  \"show\" or \"hide\"  will override the
        loading state coming from dash-renderer.

    - fullscreen (boolean; optional):
        Boolean that makes the built-in spinner display full-screen.

    - overlay_style (boolean | number | string | dict | list; optional):
        Additional CSS styling for the spinner overlay. This is applied to
        the dcc.Loading children while the spinner is active.  The default
        is `{'visibility': 'hidden'}`.

    - parent_className (string; optional):
        Additional CSS class for the outermost dcc.Loading parent div DOM
        node.

    - parent_style (boolean | number | string | dict | list; optional):
        Additional CSS styling for the outermost dcc.Loading parent div
        DOM node.

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

    - show_initially (boolean; default True):
        Whether the Spinner should show on app start-up before the loading
        state has been determined. Default True.  Use when also setting
        `delay_show`.

    - target_components (dict; optional):
        Specify component and prop to trigger showing the loading spinner
        example: `{\"output-container\": \"children\", \"grid\":
        [\"rowData\", \"columnDefs]}`.

        `target_components` is a dict with keys:


    - type (a value equal to: None, 'graph', 'cube', 'circle', 'dot', 'default'; optional):
        Property that determines which built-in spinner to show one of
        'graph', 'cube', 'circle', 'dot', or 'default'."""

    _children_props: typing.List[str] = ["custom_spinner"]
    _base_nodes = ["custom_spinner", "children"]
    _namespace = "dash_core_components"
    _type = "Loading"
    TargetComponents = TypedDict("TargetComponents", {})

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        type: typing.Optional[
            Literal[None, "graph", "cube", "circle", "dot", "default"]
        ] = None,
        fullscreen: typing.Optional[typing.Union[bool]] = None,
        debug: typing.Optional[typing.Union[bool]] = None,
        style: typing.Optional[typing.Any] = None,
        parent_className: typing.Optional[typing.Union[str]] = None,
        parent_style: typing.Optional[typing.Any] = None,
        overlay_style: typing.Optional[typing.Any] = None,
        color: typing.Optional[typing.Union[str]] = None,
        display: typing.Optional[Literal[None, "auto", "show", "hide"]] = None,
        delay_hide: typing.Optional[typing.Union[NumberType]] = None,
        delay_show: typing.Optional[typing.Union[NumberType]] = None,
        show_initially: typing.Optional[typing.Union[bool]] = None,
        target_components: typing.Optional[typing.Union["TargetComponents"]] = None,
        custom_spinner: typing.Optional[ComponentType] = None,
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
            "children",
            "id",
            "className",
            "color",
            "componentPath",
            "custom_spinner",
            "debug",
            "delay_hide",
            "delay_show",
            "display",
            "fullscreen",
            "overlay_style",
            "parent_className",
            "parent_style",
            "persisted_props",
            "persistence",
            "persistence_type",
            "show_initially",
            "style",
            "target_components",
            "type",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "className",
            "color",
            "componentPath",
            "custom_spinner",
            "debug",
            "delay_hide",
            "delay_show",
            "display",
            "fullscreen",
            "overlay_style",
            "parent_className",
            "parent_style",
            "persisted_props",
            "persistence",
            "persistence_type",
            "show_initially",
            "style",
            "target_components",
            "type",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Loading, self).__init__(children=children, **args)


setattr(Loading, "__init__", _explicitize_args(Loading.__init__))
