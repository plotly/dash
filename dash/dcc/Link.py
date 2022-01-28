# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Link(Component):
    """A Link component.
    Link allows you to create a clickable link within a multi-page app.

    For links with destinations outside the current app, `html.A` is a better
    component to use.

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The children of this component.

    - href (string; required):
        The URL of a linked resource.

    - target (string; optional):
        Specifies where to open the link reference.

    - refresh (boolean; default False):
        Controls whether or not the page will refresh when the link is
        clicked.

    - title (string; optional):
        Adds the title attribute to your link, which can contain
        supplementary information.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

    - style (dict; optional):
        Defines CSS styles which will override styles previously set.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - component_name (string; optional):
            Holds the name of the component that is loading.

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading."""

    @_explicitize_args
    def __init__(
        self,
        children=None,
        href=Component.REQUIRED,
        target=Component.UNDEFINED,
        refresh=Component.UNDEFINED,
        title=Component.UNDEFINED,
        className=Component.UNDEFINED,
        style=Component.UNDEFINED,
        id=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "href",
            "target",
            "refresh",
            "title",
            "className",
            "style",
            "id",
            "loading_state",
        ]
        self._type = "Link"
        self._namespace = "dash_core_components"
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "href",
            "target",
            "refresh",
            "title",
            "className",
            "style",
            "id",
            "loading_state",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in ["href"]:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(Link, self).__init__(children=children, **args)
