# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Clipboard(Component):
    """A Clipboard component.
    The Clipboard component copies text to the clipboard

    Keyword arguments:

    - id (string; optional):
        The ID used to identify this component.

    - className (string; optional):
        The class  name of the icon element.

    - content (string; optional):
        The text to  be copied to the clipboard if the `target_id` is
        None.

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - component_name (string; optional):
            Holds the name of the component that is loading.

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading.

    - n_clicks (number; default 0):
        The number of times copy button was clicked.

    - style (dict; optional):
        The icon's styles.

    - target_id (string | dict; optional):
        The id of target component containing text to copy to the
        clipboard. The inner text of the `children` prop will be copied to
        the clipboard.  If none, then the text from the  `value` prop will
        be copied.

    - title (string; optional):
        The text shown as a tooltip when hovering over the copy icon."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Clipboard"

    @_explicitize_args
    def __init__(
        self,
        id=Component.UNDEFINED,
        target_id=Component.UNDEFINED,
        content=Component.UNDEFINED,
        n_clicks=Component.UNDEFINED,
        title=Component.UNDEFINED,
        style=Component.UNDEFINED,
        className=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "id",
            "className",
            "content",
            "loading_state",
            "n_clicks",
            "style",
            "target_id",
            "title",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "id",
            "className",
            "content",
            "loading_state",
            "n_clicks",
            "style",
            "target_id",
            "title",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Clipboard, self).__init__(**args)
