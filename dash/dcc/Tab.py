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


class Tab(Component):
    """A Tab component.
    Part of dcc.Tabs - this is the child Tab component used to render a tabbed page.
    Its children will be set as the content of that tab, which if clicked will become visible.

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

    - disabled (boolean; default False):
        Determines if tab is disabled or not - defaults to False.

    - disabled_className (string; optional):
        Appends a class to the Tab component when it is disabled.

    - disabled_style (dict; default {color: '#d6d6d6'}):
        Overrides the default (inline) styles when disabled.

    - label (string; optional):
        The tab's label.

    - selected_className (string; optional):
        Appends a class to the Tab component when it is selected.

    - selected_style (dict; optional):
        Overrides the default (inline) styles for the Tab component when
        it is selected.

    - value (string; optional):
        Value for determining which Tab is currently selected."""

    _children_props: typing.List[str] = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Tab"

    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        label: typing.Optional[str] = None,
        value: typing.Optional[str] = None,
        disabled: typing.Optional[bool] = None,
        disabled_style: typing.Optional[dict] = None,
        disabled_className: typing.Optional[str] = None,
        className: typing.Optional[str] = None,
        selected_className: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        selected_style: typing.Optional[dict] = None,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "className",
            "disabled",
            "disabled_className",
            "disabled_style",
            "label",
            "selected_className",
            "selected_style",
            "style",
            "value",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "className",
            "disabled",
            "disabled_className",
            "disabled_style",
            "label",
            "selected_className",
            "selected_style",
            "style",
            "value",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Tab, self).__init__(children=children, **args)


setattr(Tab, "__init__", _explicitize_args(Tab.__init__))
