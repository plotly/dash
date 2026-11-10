"""Time Dash's JSON serialization of callback responses and layouts.

    python -m benchmarks.serialization.bench --out benchmarks/serialization/results.json
    python -m benchmarks.serialization.bench --case list_float+div --engine json

Every case is one large figure (``--traces`` x ``--points``) serialized with
``dash._utils.to_json``, the way a callback response or the initial layout is.
The figure alone is the reference; the other cases add something small that
orjson cannot serialize natively (a component, a ``go.Figure`` object, a
``pd.Timestamp``) or wrap the figure in a layout. See issue #4065.

Each engine runs in its own process. ``json`` blocks the orjson import, so
plotly takes its stdlib fallback exactly as on an install without orjson.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import statistics
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENGINES = ("orjson", "json")
DATA = {
    "numpy": "numpy array",
    "list_float": "list of float",
    "datetimeindex": "pd.DatetimeIndex",
    "list_datetime": "list of datetime",
}
EXTRAS = {
    "none": "figure alone",
    "div": "+ html.Div",
    "figure": "as go.Figure",
    "timestamp": "+ pd.Timestamp",
    "layout": "in a layout",
}
CASES = [f"{d}+{e}" for d in DATA for e in EXTRAS]


def label(case):
    data, extra = case.split("+")
    return f"{DATA[data]}, {EXTRAS[extra]}"


def _figure(data, traces, points):
    # pylint: disable=import-outside-toplevel
    import datetime

    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go

    rng = np.random.default_rng(0)

    def trace():
        y = rng.standard_normal(points)
        if data == "numpy":
            return go.Scatter(y=y)
        if data == "list_float":
            return go.Scatter(y=y.tolist())
        if data == "datetimeindex":
            return go.Scatter(x=pd.date_range("2024", periods=points, freq="min"), y=y)
        start = datetime.datetime(2024, 1, 1)
        x = [start + datetime.timedelta(minutes=i) for i in range(points)]
        return go.Scatter(x=x, y=y)

    return go.Figure([trace() for _ in range(traces)])


def payload(case, traces, points):
    """What Dash hands to ``to_json`` for this case."""
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    from dash import dcc, html

    data, extra = case.split("+")
    fig = _figure(data, traces, points)
    if extra == "layout":
        return html.Div([html.H1("Report"), dcc.Graph(id="graph", figure=fig)])
    response = {"graph": {"figure": fig if extra == "figure" else fig.to_plotly_json()}}
    if extra == "div":
        response["status"] = {"children": html.Div("ok")}
    elif extra == "timestamp":
        response["status"] = {"value": pd.Timestamp("2024-01-01")}
    return {"multi": True, "response": response}


def _versions():
    # pylint: disable=import-outside-toplevel
    from importlib.metadata import PackageNotFoundError, version

    out = {"python": platform.python_version()}
    for pkg in ("dash", "plotly", "orjson", "numpy", "pandas"):
        try:
            out[pkg] = version(pkg)
        except PackageNotFoundError:
            out[pkg] = None
    return out


def _require_orjson():
    try:
        import orjson  # noqa: F401 pylint: disable=import-outside-toplevel,unused-import
    except ImportError as err:
        raise SystemExit("the orjson engine needs orjson installed") from err


def worker(engine, cases, traces, points, repeat):
    if engine == "json":
        sys.modules["orjson"] = None  # type: ignore[assignment]
    else:
        _require_orjson()
    # pylint: disable-next=import-outside-toplevel
    from dash._utils import to_json

    results = {}
    for case in cases:
        value = payload(case, traces, points)
        size = len(to_json(value))
        times = []
        for _ in range(repeat):
            gc.collect()
            start = time.perf_counter()
            to_json(value)
            times.append((time.perf_counter() - start) * 1000)
        results[case] = {
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "bytes": size,
        }
        print(
            f"  {engine:6} {label(case):40} {results[case]['median']:8.1f} ms",
            file=sys.stderr,
        )
    # pylint: disable-next=import-outside-toplevel
    from _plotly_utils.optional_imports import get_module

    loaded = get_module("orjson", should_load=True) is not None
    return {"versions": _versions(), "orjson_loaded": loaded, "results": results}


def run(engines, cases, traces, points, repeat):
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            p for p in (REPO_ROOT, os.environ.get("PYTHONPATH")) if p
        ),
    }
    by_engine = {}
    for engine in engines:
        out = subprocess.run(
            [
                sys.executable,
                "-m",
                "benchmarks.serialization.bench",
                "--worker",
                engine,
                "--traces",
                str(traces),
                "--points",
                str(points),
                "--repeat",
                str(repeat),
                "--case",
                *cases,
            ],
            cwd=REPO_ROOT,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        by_engine[engine] = json.loads(out.stdout)
    versions = by_engine[engines[0]]["versions"]
    results = {
        case: {engine: run_["results"][case] for engine, run_ in by_engine.items()}
        for case in cases
    }
    return {
        "meta": {
            "traces": traces,
            "points": points,
            "repeat": repeat,
            "versions": versions,
            "orjson_loaded": {e: r["orjson_loaded"] for e, r in by_engine.items()},
            "labels": {case: label(case) for case in cases},
        },
        "results": results,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument("--engine", nargs="+", choices=ENGINES, default=list(ENGINES))
    parser.add_argument("--case", nargs="+", choices=CASES, default=CASES)
    parser.add_argument("--traces", type=int, default=10)
    parser.add_argument("--points", type=int, default=20_000)
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--out", help="write results here (JSON)")
    parser.add_argument("--worker", choices=ENGINES, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.worker:
        json.dump(
            worker(args.worker, args.case, args.traces, args.points, args.repeat),
            sys.stdout,
        )
        return 0

    data = run(args.engine, args.case, args.traces, args.points, args.repeat)
    header = f"{'case':42}" + "".join(f"{e:>10}" for e in args.engine)
    print(header)
    for case, by_engine in data["results"].items():
        print(
            f"{label(case):42}"
            + "".join(f"{by_engine[e]['median']:8.1f}ms" for e in args.engine)
        )
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
