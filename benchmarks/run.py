"""Run the Dash performance benchmarks and profile them.

Measure everything (writes results.json + a markdown summary)::

    python -m benchmarks.run --out benchmarks/results.json

Measure some scenarios::

    python -m benchmarks.run --scenario patch_append_nested initial_render_large

Compare against a saved baseline and gate on thresholds (this is what CI does)::

    python -m benchmarks.run --baseline benchmarks/baseline.json \
        --summary-md summary.md

The baseline holds absolute ms, but the baseline *ratio* gate divides out a
per-run "machine scale" (this run's time for a fixed calibration scenario over
the baseline's), so the comparison is machine-independent - the baseline can be
generated on any machine and does not flake across CI runners. See ``gate`` /
``machine_scale``.

CPU-profile a single scenario (saves a .cpuprofile loadable in Chrome DevTools
/ VS Code, and prints the hottest functions)::

    python -m benchmarks.run --profile patch_append_nested

Each scenario runs in its own ``bench_app`` subprocess serving the *production*
renderer bundle, driven by a headless Chrome. Timings come from
``performance.now()`` inside the page, aggregated across repeats as median / p90
/ max after dropping warm-up runs.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import socket
import statistics
import subprocess
import sys
import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from benchmarks.scenarios import SCENARIOS, Scenario

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLL = 0.003  # seconds between DOM polls while waiting for a scenario step


# ---------------------------------------------------------------------------
# Browser helper handed to each scenario's drive()
# ---------------------------------------------------------------------------


class Browser:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        # per-scenario scratch, e.g. cumulative child counts across repeats
        self.state: dict = {}

    def js(self, script):
        return self.driver.execute_script(script)

    def reload(self):
        self.driver.get(self.base_url)
        # React tracks an input's value through its own setter, so a plain
        # `el.value = x` is ignored by onChange. __setVal goes through the
        # native prototype setter so a dispatched 'input' reaches React.
        self.js(
            "window.__setVal = function(el, v){"
            "var d=Object.getOwnPropertyDescriptor("
            "window.HTMLInputElement.prototype,'value');"
            "d.set.call(el, v);"
            "el.dispatchEvent(new Event('input',{bubbles:true}));};"
        )

    def wait(self, expr, timeout=60):
        deadline = time.perf_counter() + timeout
        while True:
            if self.js(f"return Boolean({expr});"):
                return
            if time.perf_counter() > deadline:
                raise TimeoutError(f"timed out waiting for: {expr}")
            time.sleep(POLL)

    def render_time(self, ready_sel, timeout=60):
        """Reload already happened; return ms from navigation responseEnd to
        the ready sentinel being in the DOM (i.e. hydration time)."""
        self.wait(f"document.querySelector('{ready_sel}')", timeout)
        return float(
            self.js(
                "var nav=performance.getEntriesByType('navigation')[0];"
                "return performance.now() - (nav ? nav.responseEnd : 0);"
            )
        )

    def timed(self, trigger_js, done_expr, timeout=60):
        """Stamp t0, fire trigger_js, poll done_expr; return the in-browser ms
        measured at the moment done_expr first holds."""
        self.js("window.__bt0 = performance.now();" + trigger_js)
        deadline = time.perf_counter() + timeout
        while True:
            ms = self.js(
                f"return ({done_expr}) ? (performance.now() - window.__bt0) : -1;"
            )
            if ms is not None and ms >= 0:
                return float(ms)
            if time.perf_counter() > deadline:
                raise TimeoutError(f"timed out waiting for: {done_expr}")
            time.sleep(POLL)

    def graph_time(self):
        val = self.js(
            "return (window.dash_component_api"
            " && window.dash_component_api.callbackGraphTime) || null;"
        )
        return float(val) if val is not None else None


# ---------------------------------------------------------------------------
# Process + driver lifecycle
# ---------------------------------------------------------------------------


def _free_port():
    with contextlib.closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def serve(scenario: Scenario, params: dict, port: int, dev: bool = False):
    env = {
        **os.environ,
        "BENCH": scenario.name,
        "BENCH_PARAMS": json.dumps(params),
        "BENCH_PORT": str(port),
        "BENCH_DEV": "1" if dev else "",
    }
    proc = subprocess.Popen(
        [sys.executable, "-m", "benchmarks.bench_app"],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.perf_counter() + 40
        while True:
            with contextlib.closing(socket.socket()) as s:
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    break
            if proc.poll() is not None:
                raise RuntimeError(f"{scenario.name} app exited early")
            if time.perf_counter() > deadline:
                raise TimeoutError(f"{scenario.name} app never came up")
            time.sleep(0.05)
        yield f"http://127.0.0.1:{port}/"
    finally:
        proc.terminate()
        with contextlib.suppress(Exception):
            proc.wait(timeout=10)


def make_driver():
    opts = Options()
    for a in (
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1400,1000",
    ):
        opts.add_argument(a)
    return webdriver.Chrome(options=opts)


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def _pct(values, p):
    if not values:
        return None
    s = sorted(values)
    k = min(len(s) - 1, int(round((p / 100) * (len(s) - 1))))
    return s[k]


def summarize(series):
    """series: dict[metric] -> list of per-repeat floats (warm-up removed)."""
    out = {}
    for metric, vals in series.items():
        vals = [v for v in vals if v is not None]
        if not vals:
            continue
        third = max(1, len(vals) // 3)
        out[metric] = {
            "n": len(vals),
            "min": round(min(vals), 1),
            "median": round(statistics.median(vals), 1),
            "p90": round(_pct(vals, 90), 1),
            "max": round(max(vals), 1),
            # growth = late third vs early third; ~1 means flat, >>1 means the
            # per-op cost scales with the accumulated state (an O(total) smell).
            "growth": round(
                statistics.median(vals[-third:])
                / max(1e-6, statistics.median(vals[:third])),
                2,
            ),
        }
    return out


# ---------------------------------------------------------------------------
# Running a scenario
# ---------------------------------------------------------------------------


def run_scenario(scenario: Scenario, params: dict):
    series = defaultdict(list)
    port = _free_port()
    with serve(scenario, params, port) as url:
        driver = make_driver()
        try:
            b = Browser(driver, url)
            b.reload()
            b.wait("document.querySelector('#bench-ready')")
            total = scenario.warmup + scenario.repeats
            for i in range(total):
                metrics = scenario.drive(b, params)
                if i >= scenario.warmup:
                    for k, v in metrics.items():
                        series[k].append(v)
        finally:
            driver.quit()
    return summarize(series)


# ---------------------------------------------------------------------------
# CPU profiling (Chrome DevTools Profiler via CDP)
# ---------------------------------------------------------------------------


def profile_scenario(scenario: Scenario, params: dict, out_path: str):
    port = _free_port()
    # dev bundle => readable function names in the CPU profile.
    with serve(scenario, params, port, dev=True) as url:
        driver = make_driver()
        try:
            b = Browser(driver, url)
            b.reload()
            b.wait("document.querySelector('#bench-ready')")
            # warm up so we profile steady state, not first-run JIT
            for _ in range(max(scenario.warmup, 2)):
                scenario.drive(b, params)
            driver.execute_cdp_cmd("Profiler.enable", {})
            driver.execute_cdp_cmd("Profiler.setSamplingInterval", {"interval": 50})
            driver.execute_cdp_cmd("Profiler.start", {})
            for _ in range(max(scenario.repeats, 6)):
                scenario.drive(b, params)
            profile = driver.execute_cdp_cmd("Profiler.stop", {})["profile"]
        finally:
            driver.quit()

    with open(out_path, "w") as f:
        json.dump(profile, f)
    return profile, out_path


def profile_hot_functions(profile, top=25):
    """Aggregate self-time (via hitCount) per function from a CPU profile."""
    deltas = profile.get("timeDeltas") or []
    interval_us = statistics.median(deltas) if deltas else 0.0
    hits_by_fn: dict = defaultdict(int)
    loc_by_fn: dict = {}
    for node in profile["nodes"]:
        frame = node["callFrame"]
        short = frame.get("url", "").rsplit("/", 1)[-1]
        loc = f"{short}:{frame.get('lineNumber', '')}" if short else ""
        # Key anonymous frames by location so they don't all collapse into one
        # opaque "(anonymous)" bucket - that is usually where the time is.
        name = frame.get("functionName") or f"(anon) {loc or '?'}"
        hits_by_fn[name] += node.get("hitCount", 0)
        if name not in loc_by_fn:
            loc_by_fn[name] = loc
    total_hits = sum(hits_by_fn.values()) or 1
    ranked = sorted(hits_by_fn.items(), key=lambda kv: kv[1], reverse=True)
    lines = []
    for name, hits in ranked[:top]:
        self_ms = hits * interval_us / 1000.0
        pct = 100.0 * hits / total_hits
        lines.append((round(self_ms, 1), round(pct, 1), name, loc_by_fn[name]))
    return lines


# ---------------------------------------------------------------------------
# Threshold gating + reporting
# ---------------------------------------------------------------------------


# The baseline stores absolute milliseconds, which are machine-specific: the
# identical code runs ~2-4x slower on a shared CI runner than on a dev laptop,
# and even two "same class" runners vary run-to-run. Comparing raw ms against
# the baseline therefore flakes. So before the baseline comparison we divide out
# a per-run "machine scale" - this run's time for a fixed calibration workload
# over the baseline's time for the same workload - which makes the ratio
# machine-independent. The baseline can then be regenerated on ANY machine and
# committed as-is. The absolute warn_ms/fail_ms ceilings are left UN-scaled on
# purpose: they are generous order-of-magnitude guards, and staying absolute
# lets them still catch a global slowdown that would also drag the calibration
# workload (and so would otherwise hide inside the scale).
CALIBRATION_SCENARIO = "initial_render_small"
CALIBRATION_METRIC = "render_ms"

# Below this baseline p90 the metric is at the floor of browser timer resolution
# (e.g. graph_ms baselines are sub-millisecond), so the baseline *ratio* is
# dominated by jitter and a single slow sample reads as a 3x "regression". Skip
# the ratio gate for such metrics - the absolute warn_ms/fail_ms ceilings still
# guard them. Metrics that actually matter here are tens-to-thousands of ms.
MIN_BASELINE_MS = 5.0


def machine_scale(results, baseline):
    """This run's speed relative to the baseline machine (1.0 == same speed),
    from the calibration scenario measured in the same run. None when either
    side lacks it (e.g. a subset run that excludes it) - gating then falls back
    to a raw-ms comparison."""

    def anchor(src):
        m = (src or {}).get(CALIBRATION_SCENARIO, {}).get(CALIBRATION_METRIC, {})
        return m.get("median")

    now, base = anchor(results), anchor(baseline)
    if not now or not base:
        return None
    return now / base


def gate(results, scenarios, baseline=None):
    """Return (rows, worst, scale) where worst is 'ok' | 'warn' | 'fail'.

    A metric fails on the absolute fail_ms ceiling, or (if a baseline exists) on
    a >2x regression vs baseline p90 after normalizing out machine speed (see
    ``machine_scale``). It warns on warn_ms, or a >1.3x normalized baseline
    regression. The baseline-ratio check is skipped for metrics whose baseline
    p90 is below ``MIN_BASELINE_MS`` (sub-ms metrics are pure timer jitter; the
    absolute ceilings still guard them). ``scale`` is the machine factor that
    was divided out (None if no calibration was available)."""
    severity = {"ok": 0, "warn": 1, "fail": 2}
    scale = machine_scale(results, baseline) if baseline else None
    rows = []
    worst = "ok"
    for name, res in results.items():
        sc = scenarios[name]
        base = (baseline or {}).get(name, {})
        for metric, stats in res.items():
            p90 = stats["p90"]
            level = "ok"
            reasons = []
            fail_ms = sc.fail_ms.get(metric)
            warn_ms = sc.warn_ms.get(metric)
            if fail_ms is not None and p90 > fail_ms:
                level = "fail"
                reasons.append(f"p90 {p90}ms > fail {fail_ms}ms")
            elif warn_ms is not None and p90 > warn_ms:
                level = "warn"
                reasons.append(f"p90 {p90}ms > warn {warn_ms}ms")
            base_p90 = base.get(metric, {}).get("p90")
            if base_p90 and base_p90 >= MIN_BASELINE_MS:
                # On a 3x-slower runner every raw p90 is ~3x its baseline, so
                # divide the raw ratio by the machine scale to compare like for
                # like. Falls back to the raw ratio when no scale is available.
                ratio = p90 / base_p90
                if scale:
                    ratio /= scale
                tag = "x baseline" + (" (norm)" if scale else "")
                if ratio > 2.0:
                    level = "fail"
                    reasons.append(f"{ratio:.1f}{tag}")
                elif ratio > 1.3 and level != "fail":
                    level = "warn" if level == "ok" else level
                    reasons.append(f"{ratio:.1f}{tag}")
            if severity[level] > severity[worst]:
                worst = level
            rows.append(
                {
                    "scenario": name,
                    "metric": metric,
                    "p90": p90,
                    "median": stats["median"],
                    "growth": stats["growth"],
                    "base_p90": base.get(metric, {}).get("p90"),
                    "level": level,
                    "reasons": "; ".join(reasons),
                }
            )
    return rows, worst, scale


def markdown(rows, worst, errors=None, norm_note=None):
    icon = {"ok": "✅", "warn": "⚠️", "fail": "❌"}
    head = {
        "ok": "✅ all within thresholds",
        "warn": "⚠️ regressions to review",
        "fail": "❌ perf regression",
    }
    out = ["## Dash performance benchmarks", "", f"**{head[worst]}**", ""]
    if errors:
        out.append("**Scenarios that failed to run:**")
        out += [f"- `{name}`: {err}" for name, err in errors.items()]
        out.append("")
    out.append(
        "| | scenario | metric | p90 (ms) | median | growth | baseline p90 | note |"
    )
    out.append("|--|--|--|--:|--:|--:|--:|--|")
    order = {"fail": 0, "warn": 1, "ok": 2}
    for r in sorted(rows, key=lambda r: (order[r["level"]], r["scenario"])):
        out.append(
            f"| {icon[r['level']]} | {r['scenario']} | {r['metric']} "
            f"| {r['p90']} | {r['median']} | {r['growth']}x "
            f"| {r['base_p90'] if r['base_p90'] else '-'} | {r['reasons']} |"
        )
    out.append("")
    out.append(
        "_growth = late-third / early-third per-op time; ~1 is flat, a large "
        "value means the per-op cost scales with accumulated state._"
    )
    if norm_note:
        out.append("")
        out.append(f"_{norm_note}_")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scenario", nargs="*", help="subset of scenarios to run")
    ap.add_argument("--out", default="benchmarks/results.json")
    ap.add_argument("--summary-md", help="write a markdown summary here")
    ap.add_argument("--baseline", help="results.json to compare against")
    ap.add_argument("--profile", help="CPU-profile this one scenario and exit")
    ap.add_argument("--profile-out", default="benchmarks/profile.cpuprofile")
    args = ap.parse_args()

    if args.profile:
        sc = SCENARIOS[args.profile]
        profile, path = profile_scenario(sc, sc.params, args.profile_out)
        print(
            f"\nCPU profile saved to {path} "
            "(load in Chrome DevTools > Performance, or VS Code)\n"
        )
        print(f"Hottest functions during {sc.name}:\n")
        print(f"{'self ms':>8}  {'%':>5}  function")
        for self_ms, pct, name, loc in profile_hot_functions(profile):
            tag = f"  [{loc}]" if loc else ""
            print(f"{self_ms:>8}  {pct:>5}  {name or '(anonymous)'}{tag}")
        return 0

    names = args.scenario or list(SCENARIOS)
    results = {}
    errors = {}
    for name in names:
        sc = SCENARIOS[name]
        print(f"running {name} ...", flush=True)
        t0 = time.perf_counter()
        try:
            results[name] = run_scenario(sc, sc.params)
        except Exception as exc:  # keep the suite going if one app misbehaves
            errors[name] = f"{type(exc).__name__}: {exc}"
            print(f"  ERROR: {errors[name]}", flush=True)
            continue
        dur = time.perf_counter() - t0
        for metric, stats in results[name].items():
            print(
                f"  {metric:14s} median={stats['median']:>7}ms "
                f"p90={stats['p90']:>7}ms growth={stats['growth']}x "
                f"({dur:.0f}s)"
            )

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nwrote {args.out}")

    baseline = None
    if args.baseline and os.path.exists(args.baseline):
        with open(args.baseline) as f:
            baseline = json.load(f)

    rows, worst, scale = gate(results, SCENARIOS, baseline)
    if baseline is None:
        norm_note = None
    elif scale:
        norm_note = (
            f"machine scale vs baseline: {scale:.2f}x - divided out of the "
            "baseline ratios so they compare like for like (the absolute "
            "warn/fail ceilings are left un-scaled); calibrated on "
            f"`{CALIBRATION_SCENARIO}`."
        )
    else:
        norm_note = (
            f"baseline ratios NOT machine-normalized - `{CALIBRATION_SCENARIO}` "
            "was not in this run, so ratios below compare raw ms."
        )
    if errors:
        worst = "fail"
    md = markdown(rows, worst, errors, norm_note)
    if args.summary_md:
        with open(args.summary_md, "w") as f:
            f.write(md + "\n")
    print("\n" + md)

    return 1 if worst == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
