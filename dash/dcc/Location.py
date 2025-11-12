# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


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

    - refresh (a value equal to: 'callback-nav' | boolean; default True):
        Use `True` to navigate outside the Dash app or to manually refresh
        a page. Use `False` if the same callback that updates the Location
        component is also updating the page content - typically used in
        multi-page apps that do not use Pages. Use 'callback-nav' if you
        are updating the URL in a callback, or a different callback will
        respond to the new Location with updated content. This is typical
        with multi-page apps that use Pages. This will allow for
        navigating to a new page without refreshing the page.

    - search (string; optional):
        search in window.location - e.g., \"?myargument=1\"."""

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Location"

    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        pathname: typing.Optional[str] = None,
        search: typing.Optional[str] = None,
        hash: typing.Optional[str] = None,
        href: typing.Optional[str] = None,
        refresh: typing.Optional[typing.Union[Literal["callback-nav"], bool]] = None,
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


setattr(Location, "__init__", _explicitize_args(Location.__init__))
