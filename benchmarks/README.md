# Dash performance benchmarks

Standalone timing benchmarks for the renderer's hot paths (initial hydration,
callbacks, wildcards, Patch). Kept out of the pytest suite on purpose - timing
is noisy, so this reports rather than flaking tests. See
[`.ai/PERFORMANCE.md`](../.ai/PERFORMANCE.md) for the full methodology,
profiling guide, and findings.

## Quick start

```bash
npm run build                                   # production renderer bundle
python -m benchmarks.run                        # run everything, print a table
python -m benchmarks.run --scenario patch_append_nested   # just one
python -m benchmarks.run --profile wildcard_all_resolve   # CPU-profile one
```

## Layout

- `scenarios.py` - the scenarios (app + interaction + thresholds)
- `bench_app.py` - serves one scenario in its own process (production bundle)
- `run.py` - runner, CPU profiler, threshold gating, markdown report
- `baseline.json` - committed reference the CI job compares against

## Adding a scenario

Add a `build`/`drive` pair and register it in `scenarios.py`:

```python
def _build_x(params): ...        # returns a Dash app; ends its layout with READY
def _drive_x(b, params): ...     # returns {"metric_ms": <in-browser ms>}

scenario(
    name="x", description="...", params={...},
    warn_ms={"metric_ms": 500}, fail_ms={"metric_ms": 2000},
)((_build_x, _drive_x))
```

`b` is the browser helper (`b.timed`, `b.render_time`, `b.reload`, `b.state`,
`b.graph_time`). Every layout must end with the shared `READY` sentinel so the
harness can detect "fully hydrated". Then regenerate `baseline.json`.

## Streaming load test (`streaming/`)

How many browsers a server setup can stream to. Each setup (Flask on
gunicorn, FastAPI and Quart on uvicorn, 1 or 4 workers) serves
`streaming/load_app.py`, and simulated browsers (`streaming/client.py`) stream
from it while the count climbs until p95 frame latency passes 1 s or errors
pass 1%.

```bash
ulimit -n 65536
python -m benchmarks.streaming.load --redis-url redis://127.0.0.1:6379/0
python -m benchmarks.streaming.load --setup fastapi-uvicorn-w1 --browsers 100 1000
```

Multi-worker setups share frames through Redis and are skipped without
`--redis-url`. The server and the clients get separate CPUs (`--server-cpus`,
half the machine by default); a point where a client process hit 85% CPU is
flagged `client_bound` and ends that setup's sweep, since past that the numbers
measure the load generator.

## Publishing (`publish.py`)

`.github/workflows/benchmarks-publish.yml` measures on `dev` and pushes a static
site to the `gh-pages` branch: renderer timings on every push, the streaming
sweep weekly and on demand. Each chart has its own page under `embed/` to drop
into an `<iframe>` (`?theme=dark` or `?theme=light` to force a theme), the raw
numbers and their history are under `data/`, and `badges/` holds shields.io
endpoint badges. To build the site locally:

```bash
python -m benchmarks.publish --site /tmp/site \
    --renderer benchmarks/results.json --streaming benchmarks/streaming/results.json
```
