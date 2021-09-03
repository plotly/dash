# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


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

    @_explicitize_args
    def __init__(
        self,
        id=Component.UNDEFINED,
        interval=Component.UNDEFINED,
        disabled=Component.UNDEFINED,
        n_intervals=Component.UNDEFINED,
        max_intervals=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "id",
            "disabled",
            "interval",
            "max_intervals",
            "n_intervals",
        ]
        self._type = "Interval"
        self._namespace = "dash_core_components"
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
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in []:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(Interval, self).__init__(**args)
