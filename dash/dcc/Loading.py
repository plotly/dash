# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Loading(Component):
    """A Loading component.
    A Loading component that wraps any other component and displays a spinner until the wrapped component has rendered.

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

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading.

        - component_name (string; optional):
            Holds the name of the component that is loading.

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

    - style (dict; optional):
        Additional CSS styling for the built-in spinner root DOM node.

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

    @_explicitize_args
    def __init__(
        self,
        children=None,
        id=Component.UNDEFINED,
        type=Component.UNDEFINED,
        fullscreen=Component.UNDEFINED,
        debug=Component.UNDEFINED,
        className=Component.UNDEFINED,
        parent_className=Component.UNDEFINED,
        style=Component.UNDEFINED,
        parent_style=Component.UNDEFINED,
        overlay_style=Component.UNDEFINED,
        color=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        display=Component.UNDEFINED,
        delay_hide=Component.UNDEFINED,
        delay_show=Component.UNDEFINED,
        show_initially=Component.UNDEFINED,
        target_components=Component.UNDEFINED,
        custom_spinner=Component.UNDEFINED,
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
            "loading_state",
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
            "loading_state",
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
