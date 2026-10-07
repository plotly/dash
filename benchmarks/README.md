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

## Callback load test (`callbacks/`)

Plain callbacks over HTTP vs websocket callbacks, by backend: Flask (HTTP
only), FastAPI and Quart (both), 1 and 4 workers. Simulated browsers click
and wait for the response; the count climbs until p95 round trip passes 1 s
or errors pass 1%. Shares its runner with the streaming test
(`loadkit.py`).

```bash
python -m benchmarks.callbacks.load
python -m benchmarks.callbacks.load --setup fastapi-uvicorn-w1-ws --browsers 100 1000
python -m benchmarks.callbacks.load --kind async --work-ms 50   # like a query
```

A websocket stays on the worker that accepted it, so with several workers
each browser's callbacks all run on one worker. `--kind sync` (default) runs
plain `def` callbacks; `--work-ms` makes each
one burn that much CPU (or `asyncio.sleep` with `--kind async`).

## Browser swarm (`swarm/`)

The simulated clients above speak the wire protocols. The swarm drives real
headless Chromium instead, many users per machine and many machines, against
a deployed app, so the numbers include the renderer, its SharedWorkers and
the browser's own connection limits. Each user clicks a plain HTTP callback,
the same callback over the websocket, or a streaming callback
(`swarm/app.py`), timed in the page from the click to the DOM update.

Serve the app where it will be tested, the way it would be deployed:

```bash
SWARM_BACKEND=fastapi SWARM_REDIS_URL=redis://redis:6379/0 \
    uvicorn benchmarks.swarm.app:server --host 0.0.0.0 --port 8050 --workers 4
```

On Flask (no websocket) pass `--scenario http,stream`.

Try the swarm on one machine first (agents as local processes):

```bash
pip install playwright psutil && playwright install --only-shell chromium
python -m benchmarks.swarm.run --target http://127.0.0.1:8050 --local 2 \
    --users 10 25 --ramp 10 --duration 20
```

On a cloud, build the agent image (`swarm/Dockerfile`), push it to a
registry, start N machines with Docker that can reach the app, pull the image
on each, and list them in a hosts file (one `user@host` per line). Then from
any machine with SSH access to them:

```bash
docker build -t REGISTRY/dash-swarm-agent benchmarks/swarm && docker push REGISTRY/dash-swarm-agent
python -m benchmarks.swarm.run --target http://APP:8050 --hosts hosts.txt \
    --image REGISTRY/dash-swarm-agent --users 25 50 100 --out swarm.json
```

`--users` is per machine and per step; every agent starts at the same
wall-clock time (`--lead` seconds after the command, NTP keeps cloud clocks
close enough) and reports come back over SSH. Steps stop climbing at 1%
errors or a p95 over `--max-p95` ms (whole streams excluded: they take
frames x interval by design). An agent whose machine passed 85% CPU is
reported as `AGENT-BOUND`: give it fewer users or a bigger machine, its
numbers describe the browsers, not the server. Measured locally at 1 s think
time, a user costs about 0.05 core and up to 170 MB (RSS, an overcount);
start at about 30 users per 4 vCPU / 8 GB machine and watch the flag.

Reports from any number of agents merge exactly (`swarm/aggregate.py`):

```bash
python -m benchmarks.swarm.aggregate reports/*.json --out swarm.json
```

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
