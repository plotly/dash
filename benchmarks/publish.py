"""Build the public benchmark site from benchmark results.

    python -m benchmarks.publish --site site \\
        --renderer benchmarks/results.json \\
        --streaming benchmarks/streaming/results.json

``--site`` is a checkout of the ``gh-pages`` branch (or any directory). Each
run appends to ``data/*-history.json`` there, so the trend charts grow with
every publish, then rewrites the pages:

- ``index.html``: every chart, the numbers as tables, and how they were measured
- ``embed/<chart>.html``: one chart per page, sized to its frame, for
  ``<iframe>`` embedding (``?theme=light|dark`` forces a theme)
- ``data/<name>.json``: the latest results and their history, for anyone who
  wants to chart them their own way
- ``badges/<name>.json``: shields.io endpoint badges for READMEs

Either input may be omitted; the site keeps the last published numbers for it.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "web")
HISTORY_LIMIT = 200

# Interactive feel: p95 frame delivery under this counts as "served".
CAPACITY_P95_MS = 250

BACKEND_HUE = {"flask": 1, "fastapi": 2, "quart": 3}
WORKER_DASH = {1: "solid", 4: "dash"}


def _load(path, default):
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def _dump(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


def _append(history, entry, key):
    history = [h for h in history if h.get(key) != entry.get(key)]
    history.append(entry)
    return history[-HISTORY_LIMIT:]


# --- streaming --------------------------------------------------------------


def capacity(setup):
    """Highest measured browser count the setup served interactively, and
    whether the real limit is higher (the sweep ended, or the clients ran out
    of CPU, before the server fell behind)."""
    best = 0
    for p in setup["points"]:
        if p["client_bound"]:
            return best, True
        if p["error_rate"] > 0.01 or (p["latency_p95_ms"] or 1e9) > CAPACITY_P95_MS:
            return best, False
        best = p["browsers"]
    return best, bool(setup["points"])


def _setup_trace(setup, metric, unit):
    pts = [
        p for p in setup["points"] if not p["client_bound"] and p[metric] is not None
    ]
    return {
        "name": setup["label"],
        "hue": BACKEND_HUE.get(setup["backend"], 1),
        "dash": WORKER_DASH.get(setup["workers"], "dot"),
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
    where = (
        f"Server on {meta['server_cpus']} of {meta['cores']} cores ({meta['cpu']}),"
        f" Dash {meta['dash_version']} ({meta['commit']}), measured {meta['date'][:10]}"
    )
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
            "xaxis": {"title": "concurrent browsers"},
        },
        {
            "id": "streaming-latency",
            "title": "Streaming callbacks: p95 frame latency",
            "subtitle": f"Time from the callback yielding a frame to the browser reading it; {load}.",
            "source": where,
            "kind": "lines",
            "traces": [_setup_trace(s, "latency_p95_ms", "ms") for s in setups],
            "xaxis": {"title": "concurrent browsers", "type": "log"},
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
            "xaxis": {"title": "concurrent browsers", "type": "log"},
            "yaxis": {"title": "p95 time to first frame (ms)", "type": "log"},
        },
        {
            "id": "streaming-cpu",
            "title": "Streaming callbacks: server CPU",
            "subtitle": f"Average CPU used by the whole server process tree; {load}.",
            "source": where,
            "kind": "lines",
            "traces": [_setup_trace(s, "server_cpu_cores", "cores") for s in setups],
            "xaxis": {"title": "concurrent browsers", "type": "log"},
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
            note = (
                "client-bound"
                if p["client_bound"]
                else ("saturated" if p["saturated"] else "")
            )
            rows.append([s["label"]] + [_fmt(p.get(k), k) for k, _ in cols] + [note])
    return ["setup"] + [c for _, c in cols] + ["note"], rows


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


def streaming_badges(run):
    badges = {}
    for s in run["setups"]:
        cap, capped = capacity(s)
        badges[f"streaming-{s['name']}"] = {
            "schemaVersion": 1,
            "label": f"streaming {s['label']}",
            "message": f"{cap:,}{'+' if capped else ''} browsers",
            "color": "blue",
        }
    return badges


# --- renderer -----------------------------------------------------------------


def _descriptions():
    sys.path.insert(0, os.path.dirname(HERE))
    try:
        from benchmarks.scenarios import (
            SCENARIOS,
        )  # pylint: disable=import-outside-toplevel

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


# --- pages ----------------------------------------------------------------------


def _table(header, rows):
    head = "".join(f"<th>{html.escape(h)}</th>" for h in header)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in r) + "</tr>"
        for r in rows
    )
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def _page(title, body, depth=0, embed=False):
    up = "../" * depth
    cls = "embed" if embed else "full"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{up}style.css">
<script src="https://cdn.jsdelivr.net/npm/plotly.js-basic-dist-min@2.35.2/plotly-basic.min.js"></script>
<script src="{up}charts.js"></script>
</head>
<body class="{cls}">
{body}
</body>
</html>
"""


def _figure(chart, embed_url=None, embed=False):
    # No "<" at all inside the inline script, so no data can end it early.
    spec = json.dumps(chart).replace("<", "\\u003c")
    snippet = ""
    if embed_url:
        code = (
            f'<iframe src="{embed_url}" width="100%" height="460"'
            f' style="border:0" title="{html.escape(chart["title"])}"></iframe>'
        )
        snippet = (
            f'<details class="embed-code"><summary>Embed this chart</summary>'
            f"<pre><code>{html.escape(code)}</code></pre></details>"
        )
    title = "h1" if embed else "h3"
    home = (
        ' &middot; <a href="../index.html" target="_blank">Dash benchmarks</a>'
        if embed
        else ""
    )
    return f"""<figure class="chart">
<{title} class="chart-title">{html.escape(chart['title'])}</{title}>
<p class="chart-sub">{html.escape(chart['subtitle'])}</p>
<div class="plot" id="plot-{chart['id']}"></div>
<p class="chart-source">{html.escape(chart['source'])}{home}</p>
<script>renderChart(document.getElementById("plot-{chart['id']}"), {spec});</script>
{snippet}
</figure>"""


def build(site, base_url, streaming, renderer, renderer_history):
    charts = []
    if streaming:
        charts += streaming_charts(streaming)
    if renderer:
        charts += renderer_charts(renderer, renderer_history)

    for name in ("style.css", "charts.js"):
        shutil.copy(os.path.join(STATIC, name), os.path.join(site, name))
    os.makedirs(os.path.join(site, "embed"), exist_ok=True)
    for chart in charts:
        page = _page(
            chart["title"],
            _figure(chart, embed=True),
            depth=1,
            embed=True,
        )
        with open(
            os.path.join(site, "embed", f"{chart['id']}.html"), "w", encoding="utf-8"
        ) as f:
            f.write(page)

    def embed_url(chart):
        return f"{base_url.rstrip('/')}/embed/{chart['id']}.html"

    sections = []
    if streaming:
        sections.append(
            "<section><h2>Streaming callbacks under load</h2>"
            "<p>Simulated browsers stream from one app, one setup at a time, with the"
            " count raised until frames arrive late or fail. Each browser behaves like the"
            " renderer: one shared downlink, a long NDJSON response on ASGI and short polls"
            " on WSGI. Server and clients run on separate cores of one machine.</p>"
            + "".join(
                _figure(c, embed_url(c))
                for c in charts
                if c["id"].startswith("streaming")
            )
            + "<h3>All measurements</h3>"
            + _table(*streaming_table(streaming))
            + "</section>"
        )
    if renderer:
        sections.append(
            "<section><h2>Renderer</h2>"
            "<p>Each scenario runs as a real app in headless Chrome. Lower is better."
            " Growth compares late to early operations: near 1x is flat, higher means the"
            " cost grows with the page.</p>"
            + "".join(
                _figure(c, embed_url(c))
                for c in charts
                if c["id"].startswith("renderer")
            )
            + "<h3>All measurements</h3>"
            + _table(*renderer_table(renderer))
            + "</section>"
        )
    body = (
        "<header><h1>Dash benchmarks</h1>"
        '<p>Performance numbers for <a href="https://github.com/plotly/dash">Dash</a>,'
        ' measured by the harness in <a href="https://github.com/plotly/dash/tree/dev/benchmarks">'
        "benchmarks/</a> and published from CI. Every chart can be embedded. Raw numbers:"
        ' <a href="data/streaming-latest.json">streaming</a>'
        ' (<a href="data/streaming-history.json">history</a>),'
        ' <a href="data/renderer-latest.json">renderer</a>'
        ' (<a href="data/renderer-history.json">history</a>).</p></header>'
        + "".join(sections)
    )
    with open(os.path.join(site, "index.html"), "w", encoding="utf-8") as f:
        f.write(_page("Dash benchmarks", body))
    # Keep GitHub Pages from running the site through Jekyll.
    open(os.path.join(site, ".nojekyll"), "w", encoding="utf-8").close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--site", required=True)
    parser.add_argument("--renderer", help="results.json from benchmarks.run")
    parser.add_argument(
        "--streaming", help="results.json from benchmarks.streaming.load"
    )
    parser.add_argument("--commit", default=os.environ.get("GITHUB_SHA", "")[:9])
    parser.add_argument("--date")
    parser.add_argument(
        "--runner", default=os.environ.get("BENCH_RUNNER", "local machine")
    )
    parser.add_argument(
        "--base-url",
        default="https://plotly.github.io/dash",
        help="where the site is served, for the embed snippets",
    )
    args = parser.parse_args(argv)

    site = args.site
    data = os.path.join(site, "data")
    os.makedirs(data, exist_ok=True)

    streaming = _load(args.streaming, None)
    if streaming:
        _dump(os.path.join(data, "streaming-latest.json"), streaming)
        history = _load(os.path.join(data, "streaming-history.json"), [])
        summary = {
            "date": streaming["meta"]["date"],
            "commit": streaming["meta"]["commit"],
            "runner": streaming["meta"]["runner"],
            "capacity": {s["name"]: capacity(s)[0] for s in streaming["setups"]},
        }
        _dump(
            os.path.join(data, "streaming-history.json"),
            _append(history, summary, "date"),
        )
        for name, badge in streaming_badges(streaming).items():
            _dump(os.path.join(site, "badges", f"{name}.json"), badge)
    else:
        streaming = _load(os.path.join(data, "streaming-latest.json"), None)

    renderer_history = _load(os.path.join(data, "renderer-history.json"), [])
    results = _load(args.renderer, None)
    if results:
        import time  # pylint: disable=import-outside-toplevel

        entry = {
            "date": args.date or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "commit": args.commit,
            "runner": args.runner,
            "results": results,
        }
        renderer_history = _append(renderer_history, entry, "date")
        _dump(os.path.join(data, "renderer-latest.json"), entry)
        _dump(os.path.join(data, "renderer-history.json"), renderer_history)
    renderer = _load(os.path.join(data, "renderer-latest.json"), None)

    build(site, args.base_url, streaming, renderer, renderer_history)
    print(f"site written to {site}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
