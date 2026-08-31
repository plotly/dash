"""Platform-wide performance scenarios for Dash.

Each :class:`Scenario` bundles

* ``build(params) -> Dash`` - constructs an app that exercises one dimension of
  the platform (initial render, callbacks, wildcards, Patch, ...). Runs in a
  *subprocess* (see ``bench_app.py``), so it must not import selenium.
* ``drive(b, params) -> dict[str, float]`` - runs the interaction and returns
  named timings in milliseconds. Runs in the *harness* (see ``run.py``) and
  talks to the page only through the small ``b`` browser helper, so it needs no
  selenium import either.

Timings are taken with ``performance.now()`` *inside the browser* (see
``b.timed``), so they measure real client work - server round-trip + patch
apply + React render - without selenium's per-poll latency leaking in.

Thresholds are deliberately generous (see ``warn_ms`` / ``fail_ms``): this is a
signal for "something got materially slower", not a microbenchmark. ``fail_ms``
is meant to catch an order-of-magnitude regression; ``warn_ms`` flags a smaller
drift that is worth a look and gets surfaced as a PR comment.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from dash import ALL, Dash, Input, Output, Patch, dcc, html

# ---------------------------------------------------------------------------
# Shared building blocks
# ---------------------------------------------------------------------------


def _row(i):
    """A small component subtree (3 nodes) - closer to a real list row."""
    return html.Div(
        [html.Span(f"label {i}"), html.Span(f"value {i}", id=f"val-{i}")],
        className="row",
    )


# The last-rendered sentinel every layout ends with, so the harness can detect
# "fully hydrated" precisely regardless of what the scenario put on the page.
READY = html.Div("ready", id="bench-ready")


# ---------------------------------------------------------------------------
# Scenario definition
# ---------------------------------------------------------------------------


@dataclass
class Scenario:
    name: str
    description: str
    build: Callable[[dict], Dash]
    drive: Callable[..., dict]
    params: dict = field(default_factory=dict)
    # Thresholds keyed by metric name. Missing metric => not gated.
    warn_ms: dict = field(default_factory=dict)
    fail_ms: dict = field(default_factory=dict)
    # How many times to repeat the measured interaction (per process launch)
    # and how many leading runs to discard as warm-up.
    repeats: int = 12
    warmup: int = 2


SCENARIOS: dict[str, Scenario] = {}


def scenario(**kw):
    def register(fns):
        build, drive = fns
        sc = Scenario(build=build, drive=drive, **kw)
        SCENARIOS[sc.name] = sc
        return fns

    return register


# ===========================================================================
# 1. Initial render / hydration
# ===========================================================================


def _build_initial(params):
    app = Dash(__name__)
    n = params["n"]
    app.layout = html.Div([html.Div([_row(i) for i in range(n)], id="content"), READY])
    return app


def _drive_initial(b, params):
    # Reload a few times; measure hydration = time from the navigation response
    # to the ready sentinel being present in the DOM.
    b.reload()
    return {"render_ms": b.render_time("#bench-ready")}


scenario(
    name="initial_render_small",
    description="Hydrate a 200-row layout on load",
    params={"n": 200},
    warn_ms={"render_ms": 400},
    fail_ms={"render_ms": 1500},
    repeats=8,
    warmup=1,
)((_build_initial, _drive_initial))

scenario(
    name="initial_render_large",
    description="Hydrate a 3000-row layout on load",
    params={"n": 3000},
    warn_ms={"render_ms": 2500},
    fail_ms={"render_ms": 6000},
    repeats=6,
    warmup=1,
)((_build_initial, _drive_initial))


# ===========================================================================
# 2. Deep nesting hydration
# ===========================================================================


def _build_deep(params):
    app = Dash(__name__)
    node = READY
    for i in range(params["depth"]):
        node = html.Div(node, id=f"depth-{i}", className="wrap")
    app.layout = html.Div(node, id="content")
    return app


scenario(
    # Depth is capped at 120: Dash layouts deeper than ~250 nested components
    # fail to serialize (the JSON encoder's recursion limit), so this stays
    # well under that while still stressing per-depth hydration.
    name="deep_nesting",
    description="Hydrate a single 120-deep component chain",
    params={"depth": 120},
    warn_ms={"render_ms": 300},
    fail_ms={"render_ms": 1500},
    repeats=8,
    warmup=1,
)((_build_deep, _drive_initial))


# ===========================================================================
# 3. Patch append - top-level and nested (the append/rehydration path)
# ===========================================================================


def _build_patch_append(params):
    app = Dash(__name__)
    nested = params["nested"]
    if nested:
        container = html.Span([html.Span([], id="inner")], id="container")
    else:
        container = html.Span([], id="container")
    app.layout = html.Div([html.Button("go", id="btn", n_clicks=0), container, READY])

    @app.callback(
        Output("container", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def grow(n):
        p = Patch()
        target = p[0]["props"]["children"] if nested else p
        target.extend([html.Span(f"{n}.{i}") for i in range(params["batch"])])
        return p

    return app


def _drive_patch_append(b, params):
    # Each click appends `batch` children; measure the click when the container
    # is already large (the tail of the run), which is where an O(total)
    # regression shows. `growth_ms` is that late-append time; the harness also
    # reports how it compares to early appends via the per-repeat series.
    grown = (
        "(document.getElementById('inner')"
        "||document.getElementById('container')).childElementCount"
    )
    batch = params["batch"]
    # returns the in-browser ms for this single append
    expected = b.state.get("count", 0) + batch
    ms = b.timed(
        "document.getElementById('btn').click()",
        f"{grown} >= {expected}",
    )
    b.state["count"] = expected
    return {"append_ms": ms}


for _nested in (False, True):
    scenario(
        name=f"patch_append_{'nested' if _nested else 'toplevel'}",
        description=("Nested" if _nested else "Top-level")
        + " Patch().extend() into a growing container (per-append cost)",
        params={"nested": _nested, "batch": 200},
        warn_ms={"append_ms": 250},
        fail_ms={"append_ms": 1500},
        repeats=14,
        warmup=2,
    )((_build_patch_append, _drive_patch_append))


# ===========================================================================
# 4. Full children replacement (contrast to Patch append)
# ===========================================================================


def _build_full_replace(params):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("go", id="btn", n_clicks=0), html.Div(id="container"), READY]
    )

    @app.callback(
        Output("container", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def grow(n):
        return [html.Span(f"{i}") for i in range(n * params["batch"])]

    return app


def _drive_full_replace(b, params):
    batch = params["batch"]
    expected = b.state.get("count", 0) + batch
    ms = b.timed(
        "document.getElementById('btn').click()",
        f"document.getElementById('container').childElementCount >= {expected}",
    )
    b.state["count"] = expected
    return {"replace_ms": ms}


scenario(
    # Intentionally the slow path: returning the whole list is O(total) every
    # click, unlike Patch. Kept as a reference contrast, so its thresholds are
    # loose - we only want to catch it getting *even* slower.
    name="full_children_replace",
    description="Rebuild the whole children list from a callback each click",
    params={"batch": 200},
    warn_ms={"replace_ms": 6000},
    fail_ms={"replace_ms": 12000},
    repeats=10,
    warmup=1,
)((_build_full_replace, _drive_full_replace))


# ===========================================================================
# 5. Patch scalar update into a large list (in-place value change)
# ===========================================================================


def _build_patch_scalar(params):
    app = Dash(__name__)
    n = params["n"]
    app.layout = html.Div(
        [
            html.Button("go", id="btn", n_clicks=0),
            html.Span([html.Span(f"s{i}") for i in range(n)], id="container"),
            READY,
        ]
    )

    @app.callback(
        Output("container", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def touch(n_clicks):
        p = Patch()
        # flip a scalar on the first child - moves no component
        p[0]["props"]["children"] = f"y{n_clicks}"
        return p

    return app


def _drive_patch_scalar(b, params):
    click = b.state.get("click", 0) + 1
    ms = b.timed(
        "document.getElementById('btn').click()",
        "document.getElementById('container').firstElementChild.textContent"
        f" === 'y{click}'",
    )
    b.state["click"] = click
    return {"update_ms": ms}


scenario(
    name="patch_scalar_update_large",
    description="Patch a single scalar prop inside a 3000-child container",
    params={"n": 3000},
    warn_ms={"update_ms": 300},
    fail_ms={"update_ms": 1500},
    repeats=12,
    warmup=2,
)((_build_patch_scalar, _drive_patch_scalar))


# ===========================================================================
# 6. Callback fan-out: one input -> many outputs
# ===========================================================================


def _build_fanout(params):
    app = Dash(__name__)
    n = params["n"]
    app.layout = html.Div(
        [
            dcc.Input(id="src", value="0"),
            html.Div([html.Div(id=f"out-{i}") for i in range(n)], id="content"),
            READY,
        ]
    )

    @app.callback(
        [Output(f"out-{i}", "children") for i in range(n)],
        Input("src", "value"),
        prevent_initial_call=True,
    )
    def fan(v):
        return [f"{v}-{i}" for i in range(n)]

    return app


def _drive_fanout(b, params):
    n = params["n"]
    click = b.state.get("click", 0) + 1
    ms = b.timed(
        f"__setVal(document.getElementById('src'), '{click}')",
        f"document.getElementById('out-{n - 1}').textContent === '{click}-{n - 1}'",
    )
    b.state["click"] = click
    return {"fanout_ms": ms}


scenario(
    name="callback_fanout",
    description="One Input drives 300 Outputs through a single callback",
    params={"n": 300},
    warn_ms={"fanout_ms": 600},
    fail_ms={"fanout_ms": 2500},
    repeats=12,
    warmup=2,
)((_build_fanout, _drive_fanout))


# ===========================================================================
# 7. Wildcard (MATCH) resolution over many pattern-matched components
# ===========================================================================


def _build_wildcard(params):
    app = Dash(__name__)
    n = params["n"]
    rows = []
    for i in range(n):
        rows.append(
            html.Div(
                [
                    dcc.Input(id={"type": "in", "i": i}, value="0"),
                    html.Div(id={"type": "out", "i": i}, className="wout"),
                ]
            )
        )
    app.layout = html.Div([html.Div(rows, id="content"), READY])

    @app.callback(
        Output({"type": "out", "i": ALL}, "children"),
        Input({"type": "in", "i": ALL}, "value"),
        prevent_initial_call=True,
    )
    def each(values):
        return [f"{v}!" for v in values]

    return app


def _drive_wildcard(b, params):
    # Change one input; the ALL callback must resolve across all n components.
    click = b.state.get("click", 0) + 1
    ms = b.timed(
        f"__setVal(document.querySelectorAll('#content input')[0], '{click}')",
        f"document.querySelectorAll('.wout')[0].textContent === '{click}!'",
    )
    b.state["click"] = click
    return {
        "wildcard_ms": ms,
        # renderer-reported graph compute time for this dispatch
        "graph_ms": b.graph_time(),
    }


scenario(
    name="wildcard_all_resolve",
    description="One input change resolves an ALL callback over 400 components",
    params={"n": 400},
    warn_ms={"wildcard_ms": 800, "graph_ms": 150},
    fail_ms={"wildcard_ms": 3000, "graph_ms": 800},
    repeats=12,
    warmup=2,
)((_build_wildcard, _drive_wildcard))


# ===========================================================================
# 8. Callback graph compute (dependency graph scaling)
# ===========================================================================


def _build_graph(params):
    app = Dash(__name__)
    n = params["n"]
    # A chain: src -> c0 -> c1 -> ... plus cross links, to build a non-trivial
    # dependency graph the renderer has to resolve on each dispatch.
    app.layout = html.Div(
        [dcc.Input(id="src", value="0")]
        + [html.Div(id=f"c-{i}") for i in range(n)]
        + [READY]
    )

    for i in range(n):
        src = "src" if i == 0 else f"c-{i - 1}"

        @app.callback(
            Output(f"c-{i}", "children"),
            Input(src, "value" if i == 0 else "children"),
            prevent_initial_call=True,
        )
        def step(v, _i=i):
            return f"{v}-{_i}"

    return app


def _drive_graph(b, params):
    n = params["n"]
    click = b.state.get("click", 0) + 1
    ms = b.timed(
        f"__setVal(document.getElementById('src'), '{click}')",
        # chain concatenates: c-k = "<value>-0-1-...-k"; the last one starting
        # with this click's value means the dispatch propagated end to end.
        f"document.getElementById('c-{n - 1}').textContent.startsWith('{click}-')",
    )
    b.state["click"] = click
    return {"chain_ms": ms, "graph_ms": b.graph_time()}


scenario(
    name="callback_chain",
    description="A 100-deep callback chain resolves end to end",
    params={"n": 100},
    warn_ms={"chain_ms": 2500, "graph_ms": 100},
    fail_ms={"chain_ms": 8000, "graph_ms": 600},
    repeats=8,
    warmup=1,
)((_build_graph, _drive_graph))
