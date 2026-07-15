from typing import Any

from .development.base_component import Component

# Private, non-prop marker set by `remount` and read by the renderer
# (DashWrapper). `Component.to_plotly_json` emits it as a top-level key, so
# it never enters the component's props nor triggers prop validation.
REMOUNT_ATTR = "_dashprivate_remount"


def remount(component: Any) -> Any:
    """Force a component returned from a callback to be remounted.

    By default, when a callback returns a component that is the same (same
    ``type`` and ``id``) as the one already rendered at that position, Dash
    reconciles it in place: prop values update but the component instance is
    kept, so any internal state it holds (for example an AG Grid's selection
    or a component's transient UI state) is preserved.

    Wrapping the returned component with ``remount`` instead forces the
    renderer to unmount the existing instance and mount a fresh one,
    resetting its internal state to match what the callback returned. It is
    the explicit, opt-in equivalent of returning the component with a
    different ``id``, without having to change the ``id``.

    >>> from dash import Dash, Input, Output, callback, dcc, html, remount
    >>> @callback(Output("box", "children"), Input("btn", "n_clicks"))
    ... def cb(n):
    ...     return remount(dcc.Dropdown(id="d", options=options))
    """
    if not isinstance(component, Component):
        raise TypeError(
            "remount() expects a Dash component, got " f"{type(component).__name__}."
        )
    setattr(component, REMOUNT_ATTR, True)
    return component
