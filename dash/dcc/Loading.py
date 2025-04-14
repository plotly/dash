# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Loading(Component):
    """A Loading component.


    Keyword arguments:

    - children (list of a list of or a singular dash component, string or numbers | a list of or a singular dash component, string or number; optional):
        Array that holds components to render.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - className (string; optional):
        Additional CSS class for the built-in spinner root DOM node.

    - color (string; default '#119DFF'):
        Primary color used for the built-in loading spinners.

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

    - display (a value equal to: 'auto', 'show', 'hide'; default 'auto'):
        Setting display to  \"show\" or \"hide\"  will override the
        loading state coming from dash-renderer.

    - fullscreen (boolean; optional):
        Boolean that makes the built-in spinner display full-screen.

    - overlay_style (dict; optional):
        Additional CSS styling for the spinner overlay. This is applied to
        the dcc.Loading children while the spinner is active.  The default
        is `{'visibility': 'hidden'}`.

    - parent_className (string; optional):
        Additional CSS class for the outermost dcc.Loading parent div DOM
        node.

    - parent_style (dict; optional):
        Additional CSS styling for the outermost dcc.Loading parent div
        DOM node.

    - show_initially (boolean; default True):
        Whether the Spinner should show on app start-up before the loading
        state has been determined. Default True.  Use when also setting
        `delay_show`.

    - target_components (dict with strings as keys and values of type string | list of strings; optional):
        Specify component and prop to trigger showing the loading spinner
        example: `{\"output-container\": \"children\", \"grid\":
        [\"rowData\", \"columnDefs]}`.

    - type (a value equal to: 'graph', 'cube', 'circle', 'dot', 'default'; optional):
        Property that determines which built-in spinner to show one of
        'graph', 'cube', 'circle', 'dot', or 'default'."""

    _children_props = ["custom_spinner"]
    _base_nodes = ["custom_spinner", "children"]
    _namespace = "dash_core_components"
    _type = "Loading"

    _explicitize_dash_init = True

    def __init__(
        self,
        children: typing.Optional[
            typing.Union[
                str,
                int,
                float,
                ComponentType,
                typing.Sequence[typing.Union[str, int, float, ComponentType]],
            ]
        ] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        type: typing.Optional[
            Literal["graph", "cube", "circle", "dot", "default"]
        ] = None,
        fullscreen: typing.Optional[bool] = None,
        debug: typing.Optional[bool] = None,
        className: typing.Optional[str] = None,
        parent_className: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        parent_style: typing.Optional[dict] = None,
        overlay_style: typing.Optional[dict] = None,
        color: typing.Optional[str] = None,
        display: typing.Optional[Literal["auto", "show", "hide"]] = None,
        delay_hide: typing.Optional[
            typing.Union[
                typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
            ]
        ] = None,
        delay_show: typing.Optional[
            typing.Union[
                typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
            ]
        ] = None,
        show_initially: typing.Optional[bool] = None,
        target_components: typing.Optional[
            typing.Dict[
                typing.Union[str, float, int], typing.Union[str, typing.Sequence[str]]
            ]
        ] = None,
        custom_spinner: typing.Optional[
            typing.Union[
                str,
                int,
                float,
                ComponentType,
                typing.Sequence[typing.Union[str, int, float, ComponentType]],
            ]
        ] = None,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "className",
            "color",
            "custom_spinner",
            "debug",
            "delay_hide",
            "delay_show",
            "display",
            "fullscreen",
            "overlay_style",
            "parent_className",
            "parent_style",
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
            "custom_spinner",
            "debug",
            "delay_hide",
            "delay_show",
            "display",
            "fullscreen",
            "overlay_style",
            "parent_className",
            "parent_style",
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
