"""Turn benchmark results into the numbers the docs and the README show.

    python -m benchmarks.publish \\
        --renderer benchmarks/results.json \\
        --streaming benchmarks/streaming/results.json \\
        --callbacks benchmarks/callbacks/results.json

Writes to ``benchmarks/results/`` (``--dir``), which is committed:

- ``<name>-latest.json`` and ``<name>-history.json``: the raw numbers, and one
  summary per run so trends can be charted
- ``report.json``: every chart as a Plotly figure and the numbers as tables,
  in sections; the docs page renders it

and rewrites the table between the ``benchmarks`` markers in ``README.md``
(``--readme``). Any input may be omitted; the committed numbers for it stay.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
HISTORY_LIMIT = 200

# Interactive feel: a p95 frame delivery or callback round trip under this
# counts as "served".
CAPACITY_P95_MS = 250

BACKEND_HUE = {"flask": 1, "fastapi": 2, "quart": 3}
WORKER_DASH = {1: "solid", 4: "dash"}
TRANSPORT_HUE = {"http": 1, "ws": 2}
TRANSPORT_DASH = {"http": "solid", "ws": "dash"}
TRANSPORT_NAME = {"http": "HTTP", "ws": "websocket"}
BROWSERS_AXIS = "concurrent browsers"


def _load(path, default):
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def _read(path):
    """An input the caller named: a missing file is a mistake, not a skip."""
    if path is None:
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _dump(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
        f.write("\n")


def _append(history, entry, key):
    history = [h for h in history if h.get(key) != entry.get(key)]
    history.append(entry)
    return history[-HISTORY_LIMIT:]


# --- streaming --------------------------------------------------------------


def capacity(setup, metric="latency_p95_ms"):
    """Highest measured browser count the setup served interactively, and
    whether the real limit is higher (the sweep ended, or the clients ran out
    of CPU, before the server fell behind)."""
    best = 0
    for p in setup["points"]:
        if p["client_bound"]:
            return best, True
        if p["error_rate"] > 0.01 or (p[metric] or 1e9) > CAPACITY_P95_MS:
            return best, False
        best = p["browsers"]
    return best, bool(setup["points"])


def _setup_trace(setup, metric, unit, dash=None):
    pts = [
        p for p in setup["points"] if not p["client_bound"] and p[metric] is not None
    ]
    return {
        "name": setup["label"],
        "hue": BACKEND_HUE.get(setup["backend"], 1),
        "dash": dash or WORKER_DASH.get(setup["workers"], "dot"),
        "x": [p["browsers"] for p in pts],
        "y": [p[metric] for p in pts],
        "unit": unit,
        "saturated": [p["saturated"] for p in pts],
    }


def streaming_charts(run):
    meta, params = run["meta"], run["params"]
    load = (
        f"each browser streams {params['frames']} frames {int(params['interval'] * 1000)} ms"
        f" apart, then waits ~{params['think']:g} s and streams again"
    )
    where = _where(meta)
    setups = run["setups"]
    caps = [(s, *capacity(s)) for s in setups]
    caps.sort(key=lambda c: c[1])
    return [
        {
            "id": "streaming-capacity",
            "title": "Streaming callbacks: browsers served per server setup",
            "subtitle": (
                f"Most concurrent browsers with p95 frame latency under {CAPACITY_P95_MS} ms"
                f" and under 1% errors; {load}. A + means the sweep stopped before the"
                " server did."
            ),
            "source": where,
            "kind": "hbar",
            "bars": [
                {
                    "label": s["label"],
                    "value": cap,
                    "text": f"{cap:,}{'+' if capped else ''}",
                    "hue": 1,
                }
                for s, cap, capped in caps
            ],
            "xaxis": {"title": BROWSERS_AXIS},
        },
        {
            "id": "streaming-latency",
            "title": "Streaming callbacks: p95 frame latency",
            "subtitle": f"Time from the callback yielding a frame to the browser reading it; {load}.",
            "source": where,
            "kind": "lines",
            "traces": [_setup_trace(s, "latency_p95_ms", "ms") for s in setups],
            "xaxis": {"title": BROWSERS_AXIS, "type": "log"},
            "yaxis": {"title": "p95 latency (ms)", "type": "log"},
            "threshold": CAPACITY_P95_MS,
        },
        {
            "id": "streaming-first-frame",
            "title": "Streaming callbacks: p95 time to first frame",
            "subtitle": f"From the click (uplink POST) to the first frame on screen; {load}.",
            "source": where,
            "kind": "lines",
            "traces": [_setup_trace(s, "first_frame_p95_ms", "ms") for s in setups],
            "xaxis": {"title": BROWSERS_AXIS, "type": "log"},
            "yaxis": {"title": "p95 time to first frame (ms)", "type": "log"},
        },
        {
            "id": "streaming-cpu",
            "title": "Streaming callbacks: server CPU",
            "subtitle": f"Average CPU used by the whole server process tree; {load}.",
            "source": where,
            "kind": "lines",
            "traces": [_setup_trace(s, "server_cpu_cores", "cores") for s in setups],
            "xaxis": {"title": BROWSERS_AXIS, "type": "log"},
            "yaxis": {"title": "CPU (cores)"},
        },
    ]


def streaming_table(run):
    cols = [
        ("browsers", "browsers"),
        ("latency_p50_ms", "p50 ms"),
        ("latency_p95_ms", "p95 ms"),
        ("latency_p99_ms", "p99 ms"),
        ("first_frame_p95_ms", "first frame p95 ms"),
        ("frames_per_s", "frames/s"),
        ("error_rate", "errors"),
        ("server_cpu_cores", "server cores"),
        ("server_rss_mb", "server MB"),
    ]
    rows = []
    for s in run["setups"]:
        for p in s["points"]:
            rows.append(
                [s["label"]] + [_fmt(p.get(k), k) for k, _ in cols] + [_note(p)]
            )
    return ["setup"] + [c for _, c in cols] + ["note"], rows


def _note(point):
    if point["client_bound"]:
        return "client-bound"
    return "saturated" if point["saturated"] else ""


def _fmt(v, key=""):
    if v is None:
        return "-"
    if key == "error_rate":
        return f"{v:.1%}"
    if isinstance(v, float):
        return f"{v:,.1f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


# --- callbacks ------------------------------------------------------------------

# Server CPU is compared where every setup still keeps up.
CPU_AT_BROWSERS = 1000


def _where(meta):
    return (
        f"Server on {meta['server_cpus']} of {meta['cores']} cores ({meta['cpu']}),"
        f" Dash {meta['dash_version']} ({meta['commit']}), measured {meta['date'][:10]}"
    )


def _callback_load(params):
    work = f", each doing {params['work_ms']:g} ms of work" if params["work_ms"] else ""
    return (
        f"each browser clicks, waits for the {params['kind']} callback{work},"
        f" then waits ~{params['think']:g} s and clicks again"
    )


def callbacks_charts(run):
    params, where = run["params"], _where(run["meta"])
    load = _callback_load(params)
    setups = run["setups"]
    caps = sorted(((s, *capacity(s, "rtt_p95_ms")) for s in setups), key=lambda c: c[1])
    cpu = []
    for s in setups:
        point = next(
            (
                p
                for p in s["points"]
                if p["browsers"] == CPU_AT_BROWSERS and not p["client_bound"]
            ),
            None,
        )
        if point and point["calls_per_s"] and point["server_cpu_cores"] is not None:
            cpu.append((s, point["server_cpu_cores"] / point["calls_per_s"] * 1000))
    cpu.sort(key=lambda c: c[1])
    charts = [
        {
            "id": "callbacks-capacity",
            "title": "Callbacks: browsers served, HTTP vs websocket",
            "subtitle": (
                f"Most concurrent browsers with p95 round trip under {CAPACITY_P95_MS} ms"
                f" and under 1% errors; {load}. A + means the sweep stopped before the"
                " server did."
            ),
            "source": where,
            "kind": "hbar",
            "bars": [
                {
                    "label": s["label"],
                    "value": cap,
                    "text": f"{cap:,}{'+' if capped else ''}",
                    "hue": TRANSPORT_HUE.get(s["transport"], 1),
                }
                for s, cap, capped in caps
            ],
            "legend": [
                {"label": TRANSPORT_NAME[t], "hue": hue}
                for t, hue in TRANSPORT_HUE.items()
            ],
            "xaxis": {"title": BROWSERS_AXIS},
        }
    ]
    for workers in sorted({s["workers"] for s in setups}):
        plural = "s" if workers > 1 else ""
        charts.append(
            {
                "id": f"callbacks-rtt-w{workers}",
                "title": f"Callbacks: p95 round trip, {workers} worker{plural}",
                "subtitle": (
                    "From sending the callback to having its response, HTTP solid,"
                    f" websocket dashed; {load}."
                ),
                "source": where,
                "kind": "lines",
                "traces": [
                    _setup_trace(
                        s,
                        "rtt_p95_ms",
                        "ms",
                        dash=TRANSPORT_DASH.get(s["transport"], "dot"),
                    )
                    for s in setups
                    if s["workers"] == workers
                ],
                "xaxis": {"title": BROWSERS_AXIS, "type": "log"},
                "yaxis": {"title": "p95 round trip (ms)", "type": "log"},
                "threshold": CAPACITY_P95_MS,
            }
        )
    if cpu:
        charts.append(
            {
                "id": "callbacks-cpu",
                "title": "Callbacks: server CPU per 1,000 calls a second",
                "subtitle": (
                    f"Server CPU at {CPU_AT_BROWSERS:,} browsers divided by the calls"
                    f" it served; lower is cheaper; {load}."
                ),
                "source": where,
                "kind": "hbar",
                "bars": [
                    {
                        "label": s["label"],
                        "value": round(cores, 2),
                        "text": f"{cores:.2f} cores",
                        "hue": TRANSPORT_HUE.get(s["transport"], 1),
                    }
                    for s, cores in cpu
                ],
                "legend": [
                    {"label": TRANSPORT_NAME[t], "hue": hue}
                    for t, hue in TRANSPORT_HUE.items()
                ],
                "xaxis": {"title": "cores per 1,000 calls/s", "rangemode": "tozero"},
            }
        )
    return charts


def callbacks_table(run):
    cols = [
        ("browsers", "browsers"),
        ("rtt_p50_ms", "p50 ms"),
        ("rtt_p95_ms", "p95 ms"),
        ("rtt_p99_ms", "p99 ms"),
        ("calls_per_s", "calls/s"),
        ("error_rate", "errors"),
        ("server_cpu_cores", "server cores"),
        ("server_rss_mb", "server MB"),
    ]
    rows = []
    for s in run["setups"]:
        for p in s["points"]:
            rows.append(
                [s["label"]] + [_fmt(p.get(k), k) for k, _ in cols] + [_note(p)]
            )
    return ["setup"] + [c for _, c in cols] + ["note"], rows


# --- renderer -----------------------------------------------------------------


def _descriptions():
    sys.path.insert(0, REPO_ROOT)
    try:
        # pylint: disable-next=import-outside-toplevel
        from benchmarks.scenarios import SCENARIOS

        return {name: sc.description for name, sc in SCENARIOS.items()}
    except Exception as err:  # pylint: disable=broad-except
        print(f"warning: no scenario descriptions ({err!r})", file=sys.stderr)
        return {}


def renderer_charts(entry, history):
    desc = _descriptions()
    rows = []
    for scenario, metrics in entry["results"].items():
        for metric, stats in metrics.items():
            if stats["median"] < 5:
                continue
            rows.append((f"{scenario} ({metric})", stats, desc.get(scenario, "")))
    rows.sort(key=lambda r: r[1]["median"])
    where = (
        f"Headless Chrome, production bundle, {entry['runner']}; commit"
        f" {entry['commit']}, measured {entry['date'][:10]}"
    )
    series = {}
    for h in history:
        for scenario, metrics in h["results"].items():
            for metric, stats in metrics.items():
                key = f"{scenario} ({metric})"
                s = series.setdefault(key, {"x": [], "y": [], "commit": []})
                s["x"].append(h["date"])
                s["y"].append(stats["median"])
                s["commit"].append(h["commit"])
    order = [r[0] for r in reversed(rows)]
    return [
        {
            "id": "renderer-latest",
            "title": "Renderer: median time per interaction",
            "subtitle": (
                "In-page performance.now() timings: server round trip, patch apply and"
                " React render. Hover a bar for p90 and what it measures."
            ),
            "source": where,
            "kind": "hbar",
            "bars": [
                {
                    "label": label,
                    "value": stats["median"],
                    "text": f"{stats['median']:,.0f} ms",
                    "hover": f"{d}<br>median {stats['median']:,.1f} ms, p90 {stats['p90']:,.1f} ms,"
                    f" growth {stats.get('growth', 1):.2f}x",
                    "hue": 1,
                }
                for label, stats, d in rows
            ],
            "xaxis": {"title": "median ms (log)", "type": "log"},
        },
        {
            "id": "renderer-trend",
            "title": "Renderer: median over time",
            "subtitle": "One point per published run on the dev branch. Pick a scenario.",
            "source": where,
            "kind": "picker",
            "series": {k: series[k] for k in order if k in series},
            "yaxis": {"title": "median ms", "rangemode": "tozero"},
        },
    ]


def renderer_table(entry):
    desc = _descriptions()
    rows = []
    for scenario, metrics in entry["results"].items():
        for metric, s in metrics.items():
            rows.append(
                [
                    scenario,
                    metric,
                    _fmt(s["median"]),
                    _fmt(s["p90"]),
                    _fmt(s["max"]),
                    f"{s.get('growth', 1):.2f}x",
                    desc.get(scenario, ""),
                ]
            )
    return [
        "scenario",
        "metric",
        "median ms",
        "p90 ms",
        "max ms",
        "growth",
        "what",
    ], rows


# --- report -----------------------------------------------------------------------

# A light theme; backgrounds stay transparent so the figures sit on any page.
SERIES = {1: "#2a78d6", 2: "#eb6834", 3: "#1baf7a"}
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
LEGEND = {
    "orientation": "h",
    "x": 0,
    "y": 1.02,
    "xanchor": "left",
    "yanchor": "bottom",
    "font": {"size": 12, "color": INK_2},
}


def _axis(spec, **extra):
    spec = spec or {}
    log = spec.get("type") == "log"
    axis = {
        "title": {"text": spec.get("title", ""), "font": {"size": 12, "color": INK_2}},
        "type": spec.get("type", "linear"),
        "rangemode": spec.get("rangemode", "normal"),
        "gridcolor": GRID,
        "linecolor": AXIS,
        "zeroline": False,
        "tickfont": {"size": 11, "color": MUTED},
        "automargin": True,
    }
    if log:
        # Label the decades only (1, 10, 100, ...).
        axis["dtick"] = 1
    axis.update(extra)
    return axis


def _layout(spec):
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": 'system-ui, -apple-system, "Segoe UI", sans-serif',
            "color": INK,
        },
        "margin": {"l": 8, "r": 16, "t": 8, "b": 8},
        "xaxis": _axis(spec.get("xaxis")),
        "yaxis": _axis(spec.get("yaxis")),
        "showlegend": False,
    }


def _marker(hue):
    return {"size": 8, "color": SERIES[hue], "line": {"width": 2, "color": "#fff"}}


def _lines(spec):
    data = [
        {
            "type": "scatter",
            "mode": "lines+markers",
            "name": t["name"],
            "x": t["x"],
            "y": t["y"],
            "line": {"color": SERIES[t["hue"]], "width": 2, "dash": t["dash"]},
            "marker": _marker(t["hue"]),
            "hovertemplate": f"%{{x:,}} browsers<br>%{{y:,.1f}} {t['unit']}"
            f"<extra>{t['name']}</extra>",
        }
        for t in spec["traces"]
    ]
    layout = _layout(spec)
    # Label the x axis at the measured counts rather than log minor ticks.
    xs = sorted({x for t in spec["traces"] for x in t["x"]})
    if xs:
        layout["xaxis"].pop("dtick", None)
        layout["xaxis"]["tickvals"] = xs
        layout["xaxis"]["ticktext"] = [f"{x:,}" for x in xs]
    layout.update(showlegend=True, legend=LEGEND, hovermode="closest")
    threshold = spec.get("threshold")
    if threshold:
        log = spec.get("yaxis", {}).get("type") == "log"
        layout["shapes"] = [
            {
                "type": "line",
                "xref": "paper",
                "x0": 0,
                "x1": 1,
                "y0": threshold,
                "y1": threshold,
                "line": {"color": MUTED, "width": 1},
            }
        ]
        layout["annotations"] = [
            {
                "xref": "paper",
                "x": 0,
                "yref": "y",
                # Annotations on a log axis are placed in log units.
                "y": math.log10(threshold) if log else threshold,
                "xanchor": "left",
                "yanchor": "bottom",
                "showarrow": False,
                "text": f"{threshold} ms",
                "font": {"size": 11, "color": MUTED},
            }
        ]
    return {"data": data, "layout": layout}


def _hbar(spec):
    bars = spec["bars"]
    names = {item["hue"]: item["label"] for item in spec.get("legend", [])}
    data = []
    # One trace per colour so a legend can name them; overlaid, each bar keeps
    # its full width on its own row.
    for hue in sorted({b.get("hue", 1) for b in bars}):
        group = [b for b in bars if b.get("hue", 1) == hue]
        data.append(
            {
                "type": "bar",
                "orientation": "h",
                "name": names.get(hue, ""),
                "y": [b["label"] for b in group],
                "x": [b["value"] for b in group],
                "text": [b["text"] for b in group],
                "textposition": "outside",
                "cliponaxis": False,
                "textfont": {"size": 12, "color": INK_2},
                "marker": {"color": SERIES[hue]},
                "hovertext": [
                    b.get("hover", f"{b['label']}: {b['text']}") for b in group
                ],
                "hoverinfo": "text",
            }
        )
    layout = _layout(spec)
    layout["yaxis"] = _axis(
        {"type": "category"},
        gridcolor="rgba(0,0,0,0)",
        tickfont={"size": 12, "color": INK_2},
        categoryorder="array",
        categoryarray=[b["label"] for b in bars],
    )
    layout.update(bargap=0.35, barmode="overlay")
    layout["margin"]["r"] = 64
    if spec.get("legend"):
        layout.update(showlegend=True, legend=LEGEND)
    return {"data": data, "layout": layout}


def _picker(spec):
    """One trace per series and a dropdown that shows one at a time."""
    names = list(spec["series"])
    data = []
    for i, name in enumerate(names):
        s = spec["series"][name]
        data.append(
            {
                "type": "scatter",
                "mode": "lines+markers",
                "name": name,
                "x": s["x"],
                "y": s["y"],
                "customdata": s["commit"],
                "visible": i == 0,
                "line": {"color": SERIES[1], "width": 2},
                "marker": _marker(1),
                "hovertemplate": "%{x|%Y-%m-%d}<br>%{y:,.1f} ms<br>commit %{customdata}"
                "<extra></extra>",
            }
        )

    def x_range(series):
        if len(series["x"]) != 1:
            return {"xaxis.autorange": True}
        # One run so far: show a week around it, not a millisecond.
        day = datetime.fromisoformat(series["x"][0].replace("Z", "+00:00"))
        return {
            "xaxis.range": [
                (day - timedelta(days=3)).isoformat(),
                (day + timedelta(days=3)).isoformat(),
            ]
        }

    layout = _layout(spec)
    layout["xaxis"].update(type="date", tickformat="%b %d")
    if names:
        first = spec["series"][names[0]]
        if len(first["x"]) == 1:
            layout["xaxis"]["range"] = x_range(first)["xaxis.range"]
        layout["margin"]["t"] = 48
        layout["updatemenus"] = [
            {
                "x": 0,
                "y": 1.02,
                "xanchor": "left",
                "yanchor": "bottom",
                "buttons": [
                    {
                        "label": name,
                        "method": "update",
                        "args": [
                            {"visible": [n == name for n in names]},
                            x_range(spec["series"][name]),
                        ],
                    }
                    for name in names
                ],
            }
        ]
    return {"data": data, "layout": layout}


def figure(spec):
    """The chart spec as a Plotly figure (``data`` and ``layout``)."""
    return {"lines": _lines, "hbar": _hbar, "picker": _picker}[spec["kind"]](spec)


def _section(sid, title, intro, charts, table):
    header, rows = table
    return {
        "id": sid,
        "title": title,
        "intro": intro,
        "charts": [
            {
                "id": c["id"],
                "title": c["title"],
                "subtitle": c["subtitle"],
                "source": c["source"],
                "figure": figure(c),
            }
            for c in charts
        ],
        "table": {"header": header, "rows": rows},
    }


def report(streaming, renderer, renderer_history, callbacks=None):
    """Every chart as a Plotly figure and the numbers as tables, in sections:
    what the docs page renders."""
    sections = []
    if streaming:
        sections.append(
            _section(
                "streaming",
                "Streaming callbacks under load",
                "Simulated browsers stream from one app, one setup at a time, with the"
                " count raised until frames arrive late or fail. Each browser behaves"
                " like the renderer: one shared downlink, a long NDJSON response on ASGI"
                " and short polls on WSGI. Server and clients run on separate cores of"
                " one machine.",
                streaming_charts(streaming),
                streaming_table(streaming),
            )
        )
    if callbacks:
        sections.append(
            _section(
                "callbacks",
                "Callbacks under load: HTTP vs websocket",
                "The same callback served two ways: a POST per call, or messages on"
                " one websocket per browser (FastAPI and Quart; Flask has no"
                " websocket). Simulated browsers speak each protocol as the renderer"
                " does, and the count is raised until responses come back late or"
                " fail. Server and clients run on separate cores of one machine.",
                callbacks_charts(callbacks),
                callbacks_table(callbacks),
            )
        )
    if renderer:
        sections.append(
            _section(
                "renderer",
                "Renderer",
                "Each scenario runs as a real app in headless Chrome. Lower is better."
                " Growth compares late to early operations: near 1x is flat, higher"
                " means the cost grows with the page.",
                renderer_charts(renderer, renderer_history),
                renderer_table(renderer),
            )
        )
    return {"sections": sections}


# --- README ------------------------------------------------------------------------

README_START = "<!-- benchmarks:start -->"
README_END = "<!-- benchmarks:end -->"
NOT_MEASURED = "-"


def _server(setup):
    return (setup["backend"], setup["server"], setup["workers"])


def readme_table(streaming, callbacks):
    """Browsers each server setup keeps interactive, as a Markdown table."""
    labels, cells = {}, {}
    for s in (callbacks or {}).get("setups", []):
        key = _server(s)
        labels.setdefault(key, s["label"].rsplit(", ", 1)[0])
        cap, capped = capacity(s, "rtt_p95_ms")
        cells[key, s["transport"]] = f"{cap:,}{'+' if capped else ''}"
    for s in (streaming or {}).get("setups", []):
        key = _server(s)
        labels.setdefault(key, s["label"])
        cap, capped = capacity(s)
        cells[key, "stream"] = f"{cap:,}{'+' if capped else ''}"
    if not labels:
        return "No published run yet."
    backends = list(BACKEND_HUE)
    order = sorted(
        labels,
        key=lambda k: (
            backends.index(k[0]) if k[0] in backends else len(backends),
            k[0],
            k[2],
        ),
    )
    lines = [
        "| Server | Callbacks over HTTP | Callbacks over websocket | Streaming callbacks |",
        "|---|--:|--:|--:|",
    ]
    for key in order:
        row = [cells.get((key, col), NOT_MEASURED) for col in ("http", "ws", "stream")]
        lines.append(f"| {labels[key]} | " + " | ".join(row) + " |")
    runs = [r for r in (callbacks, streaming) if r]
    where = sorted(
        {
            f"{r['meta']['date'][:10]}: server on {r['meta']['server_cpus']} cores"
            f" ({r['meta']['runner']}), Dash {r['meta']['dash_version']}"
            for r in runs
        }
    )
    lines += [
        "",
        f"Concurrent browsers with p95 response under {CAPACITY_P95_MS} ms and under"
        " 1% errors; + means the sweep stopped before the server fell behind."
        " Flask has no websocket. Measured " + "; ".join(where) + ".",
    ]
    return "\n".join(lines)


def update_readme(path, streaming, callbacks):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    head, start, rest = text.partition(README_START)
    _, end, tail = rest.partition(README_END)
    if not start or not end:
        raise SystemExit(f"{path} has no {README_START} ... {README_END} section")
    table = readme_table(streaming, callbacks)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{head}{start}\n{table}\n{end}{tail}")


def _publish_load(run, out, name, metric):
    """Commit a load run: its numbers, and a capacity summary in its history."""
    _dump(os.path.join(out, f"{name}-latest.json"), run)
    history = _load(os.path.join(out, f"{name}-history.json"), [])
    summary = {
        "date": run["meta"]["date"],
        "commit": run["meta"]["commit"],
        "runner": run["meta"]["runner"],
        "capacity": {s["name"]: capacity(s, metric)[0] for s in run["setups"]},
    }
    _dump(os.path.join(out, f"{name}-history.json"), _append(history, summary, "date"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument("--dir", default=os.path.join(HERE, "results"))
    parser.add_argument("--readme", default=os.path.join(REPO_ROOT, "README.md"))
    parser.add_argument("--renderer", help="results.json from benchmarks.run")
    parser.add_argument(
        "--streaming", help="results.json from benchmarks.streaming.load"
    )
    parser.add_argument(
        "--callbacks", help="results.json from benchmarks.callbacks.load"
    )
    parser.add_argument("--commit", default=os.environ.get("GITHUB_SHA", "")[:9])
    parser.add_argument("--date")
    parser.add_argument(
        "--runner", default=os.environ.get("BENCH_RUNNER", "local machine")
    )
    args = parser.parse_args(argv)
    out = args.dir
    os.makedirs(out, exist_ok=True)

    for name, path, metric in (
        ("streaming", args.streaming, "latency_p95_ms"),
        ("callbacks", args.callbacks, "rtt_p95_ms"),
    ):
        run = _read(path)
        if run:
            _publish_load(run, out, name, metric)

    results = _read(args.renderer)
    if results:
        entry = {
            "date": args.date or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "commit": args.commit,
            "runner": args.runner,
            "results": results,
        }
        # The trend only charts medians; full stats stay in renderer-latest.
        trend = {
            **entry,
            "results": {
                scenario: {m: {"median": st["median"]} for m, st in metrics.items()}
                for scenario, metrics in results.items()
            },
        }
        history = _load(os.path.join(out, "renderer-history.json"), [])
        _dump(os.path.join(out, "renderer-latest.json"), entry)
        _dump(
            os.path.join(out, "renderer-history.json"),
            _append(history, trend, "date"),
        )

    streaming = _load(os.path.join(out, "streaming-latest.json"), None)
    callbacks = _load(os.path.join(out, "callbacks-latest.json"), None)
    renderer = _load(os.path.join(out, "renderer-latest.json"), None)
    renderer_history = _load(os.path.join(out, "renderer-history.json"), [])
    _dump(
        os.path.join(out, "report.json"),
        report(streaming, renderer, renderer_history, callbacks),
    )
    update_readme(args.readme, streaming, callbacks)
    print(f"results written to {out}, README table to {args.readme}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
