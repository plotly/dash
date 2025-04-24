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


class Interval(Component):
    """An Interval component.
    A component that repeatedly increments a counter `n_intervals`
    with a fixed time delay between each increment.
    Interval is good for triggering a component on a recurring basis.
    The time delay is set with the property "interval" in milliseconds.

    Keyword arguments:

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - disabled (boolean; optional):
        If True, the counter will no longer update.

    - interval (number; default 1000):
        This component will increment the counter `n_intervals` every
        `interval` milliseconds.

    - max_intervals (number; default -1):
        Number of times the interval will be fired. If -1, then the
        interval has no limit (the default) and if 0 then the interval
        stops running.

    - n_intervals (number; default 0):
        Number of times the interval has passed."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Interval"

    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        interval: typing.Optional[NumberType] = None,
        disabled: typing.Optional[bool] = None,
        n_intervals: typing.Optional[NumberType] = None,
        max_intervals: typing.Optional[NumberType] = None,
        **kwargs
    ):
        self._prop_names = [
            "id",
            "disabled",
            "interval",
            "max_intervals",
            "n_intervals",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "id",
            "disabled",
            "interval",
            "max_intervals",
            "n_intervals",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Interval, self).__init__(**args)


setattr(Interval, "__init__", _explicitize_args(Interval.__init__))
