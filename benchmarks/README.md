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
