# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Location(Component):
    """A Location component.
    Update and track the current window.location object through the window.history state.
    Use in conjunction with the `dash_core_components.Link` component to make apps with multiple pages.

    Keyword arguments:

    - id (string; required):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - hash (string; optional):
        hash in window.location - e.g., \"#myhash\".

    - href (string; optional):
        href in window.location - e.g.,
        \"/my/full/pathname?myargument=1#myhash\".

    - pathname (string; optional):
        pathname in window.location - e.g., \"/my/full/pathname\".

    - refresh (boolean; default True):
        Refresh the page when the location is updated?.

    - search (string; optional):
        search in window.location - e.g., \"?myargument=1\"."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Location"

    @_explicitize_args
    def __init__(
        self,
        id=Component.REQUIRED,
        pathname=Component.UNDEFINED,
        search=Component.UNDEFINED,
        hash=Component.UNDEFINED,
        href=Component.UNDEFINED,
        refresh=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = ["id", "hash", "href", "pathname", "refresh", "search"]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "id",
            "hash",
            "href",
            "pathname",
            "refresh",
            "search",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ["id"]:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")

        super(Location, self).__init__(**args)
