# Performance: benchmarks, profiling, and findings

Dash's user-visible speed lives almost entirely in the **renderer** (client-side
hydration, callback dispatch, Patch application). This doc covers the benchmark
harness that measures it, how to profile a slow scenario down to the hot
function, and the findings so far.

## The harness (`benchmarks/`)

A standalone harness - **not** part of the pytest suite, on purpose: timing is
noisy, so it uses generous thresholds and *reports* rather than flaking the test
matrix (see "CI job" below).

| file | role |
|--|--|
| `benchmarks/scenarios.py` | the scenarios: each has a `build(params) -> Dash` app and a `drive(b, params) -> {metric: ms}` interaction, plus warn/fail thresholds |
| `benchmarks/bench_app.py` | serves one scenario as a real app in its own process (`debug=False`, i.e. the **production** `min.js` bundle) |
| `benchmarks/run.py` | the runner + CPU profiler + threshold gating + markdown report |
| `benchmarks/baseline.json` | committed reference numbers the CI job compares against |

Each scenario runs in its own `bench_app` subprocess driven by a headless
Chrome. Timings are taken with `performance.now()` **inside the page** (not
Python-side), so they measure real client work - server round-trip + patch
apply + React render - without selenium's per-poll latency. Per scenario we drop
`warmup` runs then report **median / p90 / max** plus a **growth** ratio
(late-third ÷ early-third per-op time): `~1` is flat, a large value means the
per-op cost scales with accumulated state - an O(total) smell.

### Running locally

```bash
# prerequisites: production renderer bundle must be current
npm run build            # (or: cd dash/dash-renderer && renderer build)

# all scenarios -> results.json + a printed markdown table
python -m benchmarks.run --out benchmarks/results.json

# a subset
python -m benchmarks.run --scenario patch_append_nested wildcard_all_resolve

# gate against the committed baseline (what CI runs); exit code 1 on a hard fail
python -m benchmarks.run --baseline benchmarks/baseline.json --summary-md summary.md
```

### Updating the baseline

`baseline.json` holds absolute ms, but you do **not** need to regenerate it on a
CI-class machine: the baseline-ratio gate divides out a per-run *machine scale*
(see "Machine-independent gating" below), so a baseline captured on your laptop
compares correctly against numbers measured on a slower CI runner. Regenerate it
when scenarios change or an intended optimization lands:

```bash
python -m benchmarks.run --out benchmarks/baseline.json
```

Commit the new `baseline.json` in the same PR, and say why in the message.

To capture the baseline on CI hardware instead (so the machine scale is ~1.0x
for subsequent PRs), run the **Performance Benchmarks** workflow via
`workflow_dispatch` with `regenerate_baseline` checked, on the branch you want
to refresh (usually the default branch, right after a merge). It measures a
fresh baseline on the runner and opens a PR updating `benchmarks/baseline.json`.

### Machine-independent gating

The same code runs ~2-4x slower on a shared CI runner than on a dev machine, and
even two `ubuntu-latest` runners vary run-to-run - so comparing raw ms against a
committed baseline flakes. To avoid that, the runner measures a fixed
**calibration scenario** (`initial_render_small`) in the same run and computes a
**machine scale** = `this-run calibration median ÷ baseline calibration median`.
The baseline-ratio check then divides each scenario's raw ratio by that scale,
so a uniformly N× slower machine reports ~1.0× (no regression) while a *genuine*
regression still shows through. The scale is printed in the summary/PR comment.

The absolute `warn_ms` / `fail_ms` ceilings in `scenarios.py` are **not** scaled
- they stay generous order-of-magnitude guards and double as the backstop for a
global slowdown that would also drag the calibration workload (and so hide
inside the scale). If a run doesn't include `initial_render_small` (e.g. a
`--scenario` subset), gating falls back to a raw-ms comparison and says so.

## CI job (`.github/workflows/benchmarks.yml`)

Runs on PRs that touch `dash/`, `benchmarks/`, or components. It builds the
production bundle, runs the harness against `baseline.json`, and:

- **hard-fails** the job only on an order-of-magnitude regression - a metric
  over its absolute `fail_ms`, or `> 2x` the baseline p90 *after normalizing out
  machine speed* (see "Machine-independent gating" above);
- **warns** (without failing) on a smaller drift - over `warn_ms`, or `> 1.3x`
  the normalized baseline - and always upserts a single sticky **PR comment**
  with the table (and the machine scale) so the numbers are visible on every run;
- uploads `results.json` + `summary.md` as artifacts.

Thresholds live per-scenario in `scenarios.py` (`warn_ms` / `fail_ms`, keyed by
metric). Keep them generous: this is a smoke alarm, not a microbenchmark.

## Profiling a slow scenario

The runner can capture a **Chrome DevTools CPU profile** of a scenario and print
the hottest functions:

```bash
python -m benchmarks.run --profile wildcard_all_resolve
# -> benchmarks/profile.cpuprofile  (load in Chrome DevTools > Performance,
#    or in VS Code) + a printed "hottest functions" table
```

Profile mode serves the **dev** bundle (`dev_tools_serve_dev_bundles`, without
the rest of the dev tools) so the profile has **readable function names** -
the production bundle is minified to one-letter names. It warms up, then samples
`repeats` interactions at a 50µs sampling interval, aggregating self-time per
function by hit count.

Workflow: run the timing suite -> find a scenario with a high absolute time or
high `growth` -> `--profile` it -> read the hot functions -> the frame's
`file.dev.js:line` points straight into `dash/dash-renderer/src`.

## Findings

Numbers below are from `ubuntu-latest`-class hardware, production bundle, React
18. They move with the machine; trust the **shape** (flat vs growing, and which
function dominates), not the absolute ms.

### Snapshot (median per-op)

| scenario | median | growth | reading |
|--|--:|--:|--|
| initial_render_small (200 rows) | ~45 ms | 1.0x | fine |
| initial_render_large (3000 rows) | ~240 ms | 1.0x | linear in node count, expected |
| deep_nesting (120 deep) | ~27 ms | 1.0x | fine |
| patch_append_toplevel | ~52 ms | ~2x | flat enough; residual is shared O(total) traversal |
| patch_append_nested | ~54 ms | ~2.8x | same; the [[nested append fix]] keeps re-hydration O(appended) |
| patch_scalar_update_large (3000) | ~80 ms | ~0.8x | flat - in-place value change |
| callback_fanout (1 -> 300) | ~45 ms | 1.0x | fine |
| callback_chain (100 deep) | ~440 ms | 1.0x | ~100 sequential dispatches; inherent |
| wildcard_all_resolve (ALL over 400) | ~140 ms | 1.0x | was ~580 ms (O(n²)); now O(n), see below |
| full_children_replace (contrast) | ~850 ms | ~18x | O(total) every click *by design* - why Patch exists |

### 1. Wildcard (ALL / MATCH) resolution — was O(n²), now O(n) [fixed]

Profiling `wildcard_all_resolve` (one input change, `Output({...: ALL})` over
400 components) originally put ~45% of the time in ramda `_equals` +
`_functionName`. Root cause: `getPath` for a pattern-matching (dict) id did a
**linear** `find(propEq(values, 'values'), keyPaths)` over every component
sharing that id shape, and `propEq` is a **deep-equality** on the id-values
array. During an `ALL` resolution `getPath` is called once per resolved
component, so it was O(N) lookups × O(N) scan × O(k) equals ≈ **O(N²·k)**.

**Fix (`dash/dash-renderer/src/actions/paths.js`):** the paths table now
carries an `objIndex` - `{[keyStr]: {[valuesKey]: path}}`, where `valuesKey` is
`JSON.stringify(values)` - so `getPath` is an O(1) map lookup. `objs` stays an
ordered array because pattern matching (`resolveDeps`, `getAllPMCIds`) walks it
in order; `objIndex` is only for exact lookups. It's maintained inline in
`computePaths` (copy-on-write per keyStr, so re-resolving one chunk doesn't
rebuild the index for unrelated components) and extended incrementally in
`appendPaths`; a table without an index (empty initial state, test fixture)
makes `getPath` fall back to the linear scan, so the two never disagree.
Result: `wildcard_all_resolve` went **~580 ms → ~140 ms (≈4x)**, and the
`_equals`/`_functionName` frames left the profile. What remains is O(N) - one
`assocPath` per resolved output - which is inherent to writing N updates.

### 2. Patch append (post-fix) has no single hotspot

After the [[nested append fix]], profiling `patch_append_nested` shows the cost
spread across ramda `_path`/curry internals, React reconciliation, and redux
`useSelector` snapshots - the inherent O(total) *cheap* traversal (persistence
walk + callback crawl + element mapping), not the O(total) *re-hydration* that
the fix removed. There is no dominant frame to cut; flattening it further means
making those three traversals skip byref-unchanged subtrees (a bigger change).

### 3. Ramda currying overhead in the per-node hot loops [fixed]

Across every scenario the profiles showed ~10-15% in ramda's curry machinery -
`f1`/`f2`/`f3` (the arity dispatchers), `_isPlaceholder`, and curried `path`/
`pathOr`. It came from `crawlLayout` (utils.js), which runs the callback on
*every* component on *every* path recompute and callback gather, calling
curried `path(['props','children'], obj)` / `pathOr(...)` per node, plus the
`path(['props','id'], child)` in each crawl callback (`paths.js`,
`dependencies.js`). Replacing those with direct property access (`obj.props &&
obj.props.children`, etc.) and native array `concat` on the hot common path -
leaving the rare declared-`childrenProps` branch alone - cut `patch_append` by
~16% and initial render / wildcard by ~3-4% in a same-machine A/B. Low risk:
the crawled nodes are always plain component objects, so direct access is
equivalent to the curried `path`, just without the dispatch and placeholder
checks. When touching these traversals, prefer direct access over curried
ramda - the per-node multiplier makes it matter.

### 4. Full children replacement is the O(total) baseline

`full_children_replace` grows ~18x across a run and is ~15x slower than the
equivalent `Patch().extend()`. This is expected and is the reason `Patch`
exists for growing containers; it is kept as a contrast with loose thresholds.

### 5. Layouts deeper than ~250 nested components fail to serialize

`/_dash-layout` raises "Recursion limit reached" (the JSON encoder's recursion
limit) for a component tree nested deeper than ~254. The `deep_nesting`
scenario is capped at 120 to stay clear. Worth remembering before recommending
deeply-recursive layouts.
