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


class Markdown(Component):
    """A Markdown component.
    A component that renders Markdown text as specified by the
    GitHub Markdown spec. These component uses
    [react-markdown](https://rexxars.github.io/react-markdown/) under the hood.

    Keyword arguments:

    - children (string | list of strings; optional):
        A markdown string (or array of strings) that adheres to the
        CommonMark spec.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - className (string; optional):
        Class name of the container element.

    - dangerously_allow_html (boolean; default False):
        A boolean to control raw HTML escaping. Setting HTML from code is
        risky because it's easy to inadvertently expose your users to a
        cross-site scripting (XSS)
        (https://en.wikipedia.org/wiki/Cross-site_scripting) attack.

    - dedent (boolean; default True):
        Remove matching leading whitespace from all lines. Lines that are
        empty, or contain *only* whitespace, are ignored. Both spaces and
        tab characters are removed, but only if they match; we will not
        convert tabs to spaces or vice versa.

    - highlight_config (dict; optional):
        Config options for syntax highlighting.

        `highlight_config` is a dict with keys:

        - theme (a value equal to: 'dark', 'light'; optional):
            Color scheme; default 'light'.

    - link_target (string; optional):
        A string for the target attribute to use on links (such as
        \"_blank\").

    - mathjax (boolean; default False):
        If True, loads mathjax v3 (tex-svg) into the page and use it in
        the markdown."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Markdown"
    HighlightConfig = TypedDict(
        "HighlightConfig", {"theme": NotRequired[Literal["dark", "light"]]}
    )

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        className: typing.Optional[str] = None,
        mathjax: typing.Optional[bool] = None,
        dangerously_allow_html: typing.Optional[bool] = None,
        link_target: typing.Optional[str] = None,
        dedent: typing.Optional[bool] = None,
        highlight_config: typing.Optional["HighlightConfig"] = None,
        style: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "className",
            "dangerously_allow_html",
            "dedent",
            "highlight_config",
            "link_target",
            "mathjax",
            "style",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "className",
            "dangerously_allow_html",
            "dedent",
            "highlight_config",
            "link_target",
            "mathjax",
            "style",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Markdown, self).__init__(children=children, **args)


setattr(Markdown, "__init__", _explicitize_args(Markdown.__init__))
