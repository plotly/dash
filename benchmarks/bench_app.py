"""Serve one benchmark scenario as a real Dash app in its own process.

    BENCH=<scenario> BENCH_PARAMS='{"n": 3000}' BENCH_PORT=8090 \
        python -m benchmarks.bench_app

Run with ``debug=False`` so it serves the *production* renderer bundle
(``dash_renderer.min.js``) - that is what real users get and what we want to
measure. Build it first with ``npm run build`` (or ``renderer build``).
"""
import json
import os

from benchmarks.scenarios import SCENARIOS


def main():
    name = os.environ["BENCH"]
    params = json.loads(os.environ.get("BENCH_PARAMS", "{}"))
    port = int(os.environ.get("BENCH_PORT", "8090"))

    scenario = SCENARIOS[name]
    app = scenario.build({**scenario.params, **params})
    # threaded so many rapid callback requests don't serialize on one worker;
    # debug off => production (minified) bundle, no dev overhead. BENCH_DEV
    # serves the *un*minified bundle instead (readable function names for
    # profiling) without turning on the rest of the dev tools.
    app.run(
        host="127.0.0.1",
        port=port,
        debug=False,
        threaded=True,
        dev_tools_serve_dev_bundles=bool(os.environ.get("BENCH_DEV")),
    )


if __name__ == "__main__":
    main()
