import json
import math

import pytest

from benchmarks import publish


def _point(browsers, p95, errors=0.0, client_bound=False):
    return {
        "browsers": browsers,
        "latency_p50_ms": p95 / 2,
        "latency_p95_ms": p95,
        "latency_p99_ms": p95,
        "first_frame_p50_ms": 3.0,
        "first_frame_p95_ms": 5.0,
        "frames_per_s": 10.0,
        "streams_per_s": 1.0,
        "streams": 10,
        "frames": 200,
        "errors": 0,
        "incomplete": 0,
        "error_rate": errors,
        "server_cpu_cores": 0.5,
        "server_rss_mb": 100,
        "client_cpu_peak_pct": 99 if client_bound else 20,
        "saturated": p95 > 1000 or errors > 0.01,
        "client_bound": client_bound,
    }


def _setup(name, points):
    return {
        "name": name,
        "backend": "fastapi",
        "server": "uvicorn",
        "workers": 1,
        "label": name,
        "storage": "local",
        "points": points,
    }


def _run(setups):
    return {
        "kind": "streaming_load",
        "meta": {
            "date": "2026-10-06T00:00:00Z",
            "commit": "abc",
            "dash_version": "4.5.0",
            "python": "3.12",
            "cpu": "test cpu",
            "cores": 8,
            "memory_gb": 32,
            "server_cpus": 4,
            "client_cpus": 4,
            "runner": "test",
        },
        "params": {
            "frames": 20,
            "interval": 0.1,
            "think": 1.0,
            "ramp": 1,
            "duration": 1,
            "max_p95": 1000,
        },
        "setups": setups,
    }


def test_capacity_stops_at_first_slow_or_failing_point():
    setup = _setup("a", [_point(100, 10), _point(500, 400), _point(1000, 10)])
    assert publish.capacity(setup) == (100, False)
    assert publish.capacity(
        _setup("b", [_point(100, 10), _point(500, 10, errors=0.05)])
    ) == (100, False)


def test_capacity_marks_sweeps_that_never_saturated():
    assert publish.capacity(_setup("a", [_point(100, 10), _point(500, 20)])) == (
        500,
        True,
    )


def test_capacity_is_a_lower_bound_when_clients_ran_out_of_cpu():
    setup = _setup("a", [_point(100, 10), _point(500, 20, client_bound=True)])
    assert publish.capacity(setup) == (100, True)


README = """# Dash

### Performance

<!-- benchmarks:start -->
No published run yet.
<!-- benchmarks:end -->

### Next
"""


def _readme(tmp_path):
    path = tmp_path / "README.md"
    path.write_text(README)
    return path


def _renderer_results(tmp_path):
    path = tmp_path / "renderer.json"
    path.write_text(
        json.dumps(
            {
                "callback_fanout": {
                    "fanout_ms": {
                        "n": 3,
                        "min": 1,
                        "median": 80.0,
                        "p90": 90.0,
                        "max": 95.0,
                        "growth": 1.0,
                    }
                }
            }
        )
    )
    return path


def test_publish_commits_numbers_history_report_and_readme(tmp_path):
    streaming = tmp_path / "streaming.json"
    streaming.write_text(
        json.dumps(_run([_setup("fastapi-uvicorn-w1", [_point(100, 10)])]))
    )
    renderer = _renderer_results(tmp_path)
    readme = _readme(tmp_path)
    out = tmp_path / "results"

    for date in ("2026-10-01T00:00:00Z", "2026-10-02T00:00:00Z"):
        publish.main(
            [
                "--dir",
                str(out),
                "--readme",
                str(readme),
                "--renderer",
                str(renderer),
                "--streaming",
                str(streaming),
                "--date",
                date,
            ]
        )

    history = json.loads((out / "renderer-history.json").read_text())
    assert [h["date"][:10] for h in history] == ["2026-10-01", "2026-10-02"]
    assert history[0]["results"] == {"callback_fanout": {"fanout_ms": {"median": 80.0}}}
    latest = json.loads((out / "renderer-latest.json").read_text())
    assert latest["results"]["callback_fanout"]["fanout_ms"]["p90"] == 90.0
    assert json.loads((out / "streaming-latest.json").read_text())["setups"]
    sections = json.loads((out / "report.json").read_text())["sections"]
    assert [s["id"] for s in sections] == ["streaming", "renderer"]
    charts = [c["id"] for s in sections for c in s["charts"]]
    assert charts == [
        "streaming-capacity",
        "streaming-latency",
        "streaming-first-frame",
        "streaming-cpu",
        "renderer-latest",
        "renderer-trend",
    ]
    for s in sections:
        assert s["table"]["rows"]
        for c in s["charts"]:
            assert c["figure"]["data"] and c["figure"]["layout"]
    text = readme.read_text()
    assert "| fastapi-uvicorn-w1 | - | - | 100+ |" in text
    assert "No published run yet." not in text
    assert text.endswith("<!-- benchmarks:end -->\n\n### Next\n")


def test_lines_figure_marks_the_threshold_in_log_units():
    chart = publish.streaming_charts(
        _run([_setup("a", [_point(100, 10), _point(500, 20)])])
    )[1]
    fig = publish.figure(chart)
    assert [t["x"] for t in fig["data"]] == [[100, 500]]
    assert fig["layout"]["xaxis"]["ticktext"] == ["100", "500"]
    assert fig["layout"]["shapes"][0]["y0"] == publish.CAPACITY_P95_MS
    assert fig["layout"]["annotations"][0]["y"] == pytest.approx(
        math.log10(publish.CAPACITY_P95_MS)
    )


def test_trend_figure_shows_one_scenario_at_a_time():
    entry = {
        "date": "2026-10-01T00:00:00Z",
        "commit": "abc",
        "runner": "test",
        "results": {
            "a": {"m": {"median": 10.0, "p90": 12.0, "max": 13.0}},
            "b": {"m": {"median": 20.0, "p90": 22.0, "max": 23.0}},
        },
    }
    trend = publish.renderer_charts(entry, [entry])[1]
    fig = publish.figure(trend)
    # Slowest scenario first.
    assert [(t["name"], t["visible"]) for t in fig["data"]] == [
        ("b (m)", True),
        ("a (m)", False),
    ]
    buttons = fig["layout"]["updatemenus"][0]["buttons"]
    assert [b["args"][0]["visible"] for b in buttons] == [[True, False], [False, True]]
    # A single run gets a week of axis, not a millisecond.
    assert "xaxis.range" in buttons[0]["args"][1]


def test_named_input_must_exist(tmp_path):
    with pytest.raises(FileNotFoundError):
        publish.main(
            [
                "--dir",
                str(tmp_path / "results"),
                "--readme",
                str(_readme(tmp_path)),
                "--streaming",
                str(tmp_path / "typo.json"),
            ]
        )


def test_readme_names_each_run_and_sorts_unknown_backends_last():
    callbacks = _cb_run()
    streaming = _run(
        [{**_setup("starlette-uvicorn-w1", [_point(100, 10)]), "backend": "starlette"}]
    )
    streaming["meta"] = {**streaming["meta"], "date": "2026-10-07T00:00:00Z"}
    lines = publish.readme_table(streaming, callbacks).splitlines()
    assert lines[-3].startswith("| starlette-uvicorn-w1 |")
    assert lines[-1].endswith(
        "Measured 2026-10-06: server on 4 cores (test), Dash 4.5.0;"
        " 2026-10-07: server on 4 cores (test), Dash 4.5.0."
    )


def test_readme_needs_its_markers(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Dash\n")
    with pytest.raises(SystemExit):
        publish.update_readme(str(readme), None, None)


def _cb_point(browsers, p95, calls_per_s=100.0, cores=0.2, client_bound=False):
    return {
        "browsers": browsers,
        "rtt_p50_ms": p95 / 2,
        "rtt_p95_ms": p95,
        "rtt_p99_ms": p95,
        "calls_per_s": calls_per_s,
        "calls": int(calls_per_s * 20),
        "errors": 0,
        "failed_browsers": 0,
        "error_rate": 0.0,
        "server_cpu_cores": cores,
        "server_rss_mb": 100,
        "client_cpu_peak_pct": 99 if client_bound else 20,
        "saturated": p95 > 1000,
        "client_bound": client_bound,
    }


def _cb_run():
    def setup(name, backend, workers, transport, points):
        return {
            "name": name,
            "backend": backend,
            "server": "uvicorn",
            "workers": workers,
            "label": name,
            "transport": transport,
            "points": points,
        }

    run = _run(
        [
            setup(
                "fastapi-w1-http",
                "fastapi",
                1,
                "http",
                [_cb_point(100, 2), _cb_point(1000, 300, 900, 0.9)],
            ),
            setup(
                "fastapi-w1-ws",
                "fastapi",
                1,
                "ws",
                [_cb_point(100, 1), _cb_point(1000, 5, 1000, 0.3)],
            ),
            setup("quart-w4-ws", "quart", 4, "ws", [_cb_point(100, 1)]),
        ]
    )
    run["kind"] = "callback_load"
    run["params"] = {
        "kind": "sync",
        "work_ms": 0.0,
        "think": 1.0,
        "ramp": 1,
        "duration": 1,
        "max_p95": 1000,
    }
    return run


def test_callback_charts_split_by_transport_and_workers():
    charts = {c["id"]: c for c in publish.callbacks_charts(_cb_run())}
    assert set(charts) == {
        "callbacks-capacity",
        "callbacks-rtt-w1",
        "callbacks-rtt-w4",
        "callbacks-cpu",
    }
    bars = {b["label"]: b for b in charts["callbacks-capacity"]["bars"]}
    assert bars["fastapi-w1-http"]["text"] == "100"
    assert bars["fastapi-w1-ws"]["text"] == "1,000+"
    assert bars["fastapi-w1-ws"]["hue"] != bars["fastapi-w1-http"]["hue"]
    w1 = charts["callbacks-rtt-w1"]["traces"]
    assert [t["dash"] for t in w1] == ["solid", "dash"]
    cpu = {b["label"]: b["value"] for b in charts["callbacks-cpu"]["bars"]}
    # Only setups measured at 1,000 browsers are compared.
    assert cpu == {"fastapi-w1-ws": 0.3, "fastapi-w1-http": 1.0}


def test_readme_table_has_one_row_per_server():
    streaming = _run(
        [
            {
                **_setup("fastapi-uvicorn-w1", [_point(100, 10), _point(500, 400)]),
                "label": "FastAPI, uvicorn 1 worker",
            }
        ]
    )
    callbacks = _cb_run()
    for s in callbacks["setups"]:
        s["label"] = {
            "fastapi-w1-http": "FastAPI, uvicorn 1 worker, HTTP",
            "fastapi-w1-ws": "FastAPI, uvicorn 1 worker, websocket",
            "quart-w4-ws": "Quart, uvicorn 4 workers, websocket",
        }[s["name"]]
    lines = publish.readme_table(streaming, callbacks).splitlines()
    assert lines[2:4] == [
        "| FastAPI, uvicorn 1 worker | 100 | 1,000+ | 100 |",
        "| Quart, uvicorn 4 workers | - | 100+ | - |",
    ]
    assert lines[-1].endswith(
        "Measured 2026-10-06: server on 4 cores (test), Dash 4.5.0."
    )


def test_publish_keeps_committed_callbacks_when_not_given(tmp_path):
    callbacks = tmp_path / "callbacks.json"
    callbacks.write_text(json.dumps(_cb_run()))
    out = tmp_path / "results"
    readme = _readme(tmp_path)
    args = ["--dir", str(out), "--readme", str(readme)]
    publish.main([*args, "--callbacks", str(callbacks)])
    publish.main(args)
    sections = json.loads((out / "report.json").read_text())["sections"]
    assert [s["title"] for s in sections] == ["Callbacks under load: HTTP vs websocket"]
    assert "| fastapi-w1-http | 100 | 1,000+ | - |" in readme.read_text()
    history = json.loads((out / "callbacks-history.json").read_text())
    assert len(history) == 1
    assert history[0]["capacity"]["fastapi-w1-http"] == 100


def _stats(median):
    return {"n": 3, "min": 1, "median": median, "p90": median, "max": median}


def test_median_change_must_beat_both_noise_floors():
    old = {"results": {"a": {"m": _stats(100.0)}, "b": {"m": _stats(4.0)}}}

    def changes(new):
        return publish.median_changes("renderer", old, new, 5.0)

    # +20 ms but only 20%: noise.
    assert changes({"a": {"m": _stats(120.0)}}) == []
    # +100% but only 4 ms: noise.
    assert changes({"b": {"m": _stats(8.0)}}) == []
    assert changes({"a": {"m": _stats(130.0)}}) == ["renderer a (m): 100.0 -> 130.0 ms"]
    assert changes({"c": {"m": _stats(7.0)}}) == ["renderer c (m): new, 7.0 ms"]


def _serialization_run(div_ms):
    def stats(median):
        return {"median": median, "min": median, "max": median, "bytes": 1000}

    return {
        "meta": {
            "traces": 10,
            "points": 20000,
            "repeat": 7,
            "versions": {
                "python": "3.12.0",
                "dash": "4.5.0",
                "plotly": "6.7.0",
                "orjson": "3.11.0",
            },
            "labels": {
                "list_float+none": "list of float, figure alone",
                "list_float+div": "list of float, + html.Div",
            },
        },
        "results": {
            "list_float+none": {"orjson": stats(6.0), "json": stats(50.0)},
            "list_float+div": {"orjson": stats(div_ms), "json": stats(51.0)},
        },
    }


def test_serialization_section_compares_each_case_to_the_figure_alone(tmp_path):
    out = tmp_path / "results"
    run = tmp_path / "serialization.json"
    changes = tmp_path / "changes.md"
    args = ["--dir", str(out), "--readme", str(_readme(tmp_path)), "--only-significant"]

    run.write_text(json.dumps(_serialization_run(40.0)))
    publish.main([*args, "--serialization", str(run), "--date", "2026-10-01T00:00:00Z"])
    sections = json.loads((out / "report.json").read_text())["sections"]
    assert [s["id"] for s in sections] == ["serialization"]
    section = sections[0]
    assert [c["id"] for c in section["charts"]] == [
        "serialization-orjson",
        "serialization-json",
        "serialization-trend",
    ]
    orjson_bars = section["charts"][0]["figure"]["data"]
    assert [t["name"] for t in orjson_bars] == [
        "figure alone",
        "same figure, plus one non-native value",
    ]
    assert orjson_bars[1]["x"] == [40.0]
    assert section["table"]["rows"][1][:3] == [
        "list of float, + html.Div",
        "40.0",
        "6.7x",
    ]
    latest = json.loads((out / "serialization-latest.json").read_text())
    assert latest["versions"]["plotly"] == "6.7.0"
    assert latest["date"] == "2026-10-01T00:00:00Z"

    # A plotly fix that drops the + html.Div case to the figure-alone time.
    fixed = _serialization_run(6.5)
    fixed["meta"]["versions"]["plotly"] = "6.8.0"
    run.write_text(json.dumps(fixed))
    publish.main(
        [
            *args,
            "--serialization",
            str(run),
            "--date",
            "2026-10-08T00:00:00Z",
            "--changes",
            str(changes),
        ]
    )
    assert changes.read_text() == (
        "- serialization list_float+div (orjson): 40.0 -> 6.5 ms\n"
        "- serialization measured with plotly 6.8.0 (was 6.7.0)\n"
    )
    history = json.loads((out / "serialization-history.json").read_text())
    assert [h["results"]["list_float+div"]["orjson"] for h in history] == [
        {"median": 40.0},
        {"median": 6.5},
    ]
    trend = json.loads((out / "report.json").read_text())["sections"][0]["charts"][2]
    assert (
        trend["figure"]["data"][0]["name"] == "list of float, figure alone, with orjson"
    )


def test_load_change_is_a_capacity_step():
    old = _run([_setup("a", [_point(100, 10), _point(500, 400)])])
    same = _run([_setup("a", [_point(100, 50), _point(500, 900)])])
    assert publish.load_changes("streaming", old, same, "latency_p95_ms") == []
    better = _run([_setup("a", [_point(100, 10), _point(500, 20)])])
    assert publish.load_changes("streaming", old, better, "latency_p95_ms") == [
        "streaming a: 100 -> 500+ browsers"
    ]
    assert publish.load_changes("streaming", None, old, "latency_p95_ms") == [
        "streaming: first published run"
    ]


def test_only_significant_runs_are_committed(tmp_path):
    out = tmp_path / "results"
    readme = _readme(tmp_path)
    run = tmp_path / "streaming.json"
    changes = tmp_path / "changes.md"
    args = ["--dir", str(out), "--readme", str(readme), "--only-significant"]

    run.write_text(json.dumps(_run([_setup("a", [_point(100, 10)])])))
    publish.main([*args, "--streaming", str(run), "--changes", str(changes)])
    assert changes.read_text() == "- streaming: first published run\n"
    first = readme.read_text()

    # Slower but still inside the same capacity step: nothing is written.
    later = _run([_setup("a", [_point(100, 60)])])
    later["meta"]["date"] = "2026-10-13T00:00:00Z"
    run.write_text(json.dumps(later))
    publish.main([*args, "--streaming", str(run), "--changes", str(changes)])
    assert changes.read_text() == ""
    assert readme.read_text() == first
    assert len(json.loads((out / "streaming-history.json").read_text())) == 1

    later["setups"][0]["points"].append(_point(500, 20))
    run.write_text(json.dumps(later))
    publish.main([*args, "--streaming", str(run), "--changes", str(changes)])
    assert changes.read_text() == "- streaming a: 100+ -> 500+ browsers\n"
    assert "| a | - | - | 500+ |" in readme.read_text()
    assert len(json.loads((out / "streaming-history.json").read_text())) == 2
