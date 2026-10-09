import json

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


def test_inline_chart_data_cannot_close_its_script():
    chart = {
        "id": "x",
        "title": "t",
        "subtitle": "s",
        "source": "src",
        "kind": "hbar",
        "bars": [{"label": "<!--<script></script>", "value": 1, "text": "1"}],
    }
    script = publish._figure(chart).split("<script>")[1].split("</script>")[0]
    assert "<" not in script


def test_site_has_embeds_data_badges_and_history(tmp_path):
    streaming = tmp_path / "streaming.json"
    streaming.write_text(
        json.dumps(_run([_setup("fastapi-uvicorn-w1", [_point(100, 10)])]))
    )
    renderer = tmp_path / "renderer.json"
    renderer.write_text(
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
    site = tmp_path / "site"

    for date in ("2026-10-01T00:00:00Z", "2026-10-02T00:00:00Z"):
        publish.main(
            [
                "--site",
                str(site),
                "--renderer",
                str(renderer),
                "--streaming",
                str(streaming),
                "--date",
                date,
                "--base-url",
                "https://example.test/dash",
            ]
        )

    for chart in (
        "streaming-capacity",
        "streaming-latency",
        "renderer-latest",
        "renderer-trend",
    ):
        page = (site / "embed" / f"{chart}.html").read_text()
        assert "renderChart(" in page
        assert "../charts.js" in page
    index = (site / "index.html").read_text()
    assert "https://example.test/dash/embed/streaming-capacity.html" in index
    badge = json.loads(
        (site / "badges" / "streaming-fastapi-uvicorn-w1.json").read_text()
    )
    assert badge["message"] == "100+ browsers"
    history = json.loads((site / "data" / "renderer-history.json").read_text())
    assert [h["date"][:10] for h in history] == ["2026-10-01", "2026-10-02"]
    assert (site / ".nojekyll").exists()


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


def test_site_keeps_published_callbacks_when_not_given(tmp_path):
    callbacks = tmp_path / "callbacks.json"
    callbacks.write_text(json.dumps(_cb_run()))
    site = tmp_path / "site"
    publish.main(["--site", str(site), "--callbacks", str(callbacks)])
    publish.main(["--site", str(site)])
    index = (site / "index.html").read_text()
    assert "HTTP vs websocket" in index
    assert (site / "embed" / "callbacks-capacity.html").exists()
    badge = json.loads((site / "badges" / "callbacks-fastapi-w1-ws.json").read_text())
    assert badge["message"] == "1,000+ browsers"
    history = json.loads((site / "data" / "callbacks-history.json").read_text())
    assert history[0]["capacity"]["fastapi-w1-http"] == 100
