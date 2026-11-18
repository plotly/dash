"""One machine's share of a browser swarm: real headless Chromium users.

Each user is its own browser context (own cookies, cache and SharedWorkers,
like a separate person) in one of ``--browsers`` Chromium processes. A user
loads the page, then loops: click one of the scenarios, wait for its output,
think, click again. Timings are taken inside the page with
``performance.now()``, from just before the click to the DOM update a person
would see, so they include the renderer and need no clock agreement between
machines. Only the start time is shared (``--start-at``, wall clock; NTP is
close enough).

Scenarios (``--scenario``, picked at random per click):

- ``http``: a plain callback over HTTP.
- ``ws``: the same callback over the websocket.
- ``stream``: a streaming callback; records first frame and whole stream.

Writes one JSON report (``--out``) with mergeable histograms; combine the
swarm's reports with ``benchmarks.swarm.aggregate``. The report also carries
the agent machine's CPU during the window: past ~85% the browsers themselves
are the bottleneck and the numbers describe this machine, not the server.

Needs only ``playwright`` (with Chromium) and ``psutil``, not dash.
"""
import argparse
import asyncio
import contextlib
import json
import math
import os
import random
import socket
import sys
import time

import psutil
from playwright.async_api import async_playwright

try:
    from .histogram import Histogram
except ImportError:
    # Run as a script inside the agent image, where there is no package.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from histogram import Histogram  # type: ignore[no-redef]

ACTION_TIMEOUT = 30
LOAD_TIMEOUT = 60

# Click a scenario's button and resolve once its output shows the result for
# this click: "clicked <n>" for a callback, "<n>:<last> done" for a stream.
CLICK_AND_WAIT = """
async ([name, n]) => {
    const out = document.getElementById(name + '-out');
    const btn = document.getElementById(name + '-btn');
    return await new Promise((resolve) => {
        let first = null;
        const t0 = performance.now();
        const check = () => {
            const text = out.textContent;
            if (name === 'stream') {
                if (!text.startsWith(n + ':')) return;
                const now = performance.now() - t0;
                if (first === null) first = now;
                if (text.endsWith(' done')) {
                    obs.disconnect();
                    resolve({first, total: now});
                }
            } else if (text === 'clicked ' + n) {
                obs.disconnect();
                resolve({total: performance.now() - t0});
            }
        };
        const obs = new MutationObserver(check);
        obs.observe(out, {childList: true, subtree: true, characterData: true});
        btn.click();
    });
}
"""


class Report:
    def __init__(self, measure_from, measure_to):
        self.measure_from = measure_from
        self.measure_to = measure_to
        self.hists = {}
        self.counts = {
            "actions": 0,
            "errors": 0,
            "page_errors": 0,
            "users_failed": 0,
            "reloads": 0,
        }
        self.errors_by_kind = {}

    def in_window(self, t):
        return self.measure_from <= t <= self.measure_to

    def add(self, metric, ms):
        self.hists.setdefault(metric, Histogram()).add(ms)

    def error(self, kind):
        self.counts["errors"] += 1
        self.errors_by_kind[kind] = self.errors_by_kind.get(kind, 0) + 1


class User:
    def __init__(self, browser, args, report):
        self.browser = browser
        self.args = args
        self.report = report
        self.page = None
        self.clicks = {}

    async def load(self):
        # The page restarts its click counts whether or not the load succeeds.
        self.clicks = {}
        await self.page.goto(self.args.target, timeout=LOAD_TIMEOUT * 1000)
        await self.page.wait_for_selector(
            "#ready", state="attached", timeout=LOAD_TIMEOUT * 1000
        )
        if "ws" in self.args.scenario and not await self.page.evaluate(
            "() => !!JSON.parse("
            "document.getElementById('_dash-config').textContent).websocket"
        ):
            raise RuntimeError("no websocket on this backend: drop the ws scenario")

    async def act(self, scenario):
        n = self.clicks.get(scenario, 0) + 1
        self.clicks[scenario] = n
        return await asyncio.wait_for(
            self.page.evaluate(CLICK_AND_WAIT, [scenario, n]), ACTION_TIMEOUT
        )

    async def _start(self):
        """Open this user's context and load the page; None if it failed.
        A user that never starts is counted whenever it happens: it takes its
        share of the load away from the whole run."""
        context = None
        try:
            context = await self.browser.new_context()
            self.page = await context.new_page()

            def on_page_error(_err):
                self.report.counts["page_errors"] += 1

            self.page.on("pageerror", on_page_error)
            started = time.time()
            await self.load()
            # The first load happens during the ramp, so it is not windowed.
            self.report.add("page_load", (time.time() - started) * 1000)
            return context
        except Exception:  # pylint: disable=broad-except
            self.report.counts["users_failed"] += 1
            self.report.error("page_load")
            if context is not None:
                with contextlib.suppress(Exception):
                    await context.close()
            return None

    async def _reload(self):
        """Start the page over after an error; False if that failed too."""
        self.report.counts["reloads"] += 1
        attempted = time.time()
        try:
            await self.load()
            return True
        except Exception:  # pylint: disable=broad-except
            if self.report.in_window(attempted):
                self.report.error("reload")
            await asyncio.sleep(1)
            return False

    async def _click(self, scenario):
        """One timed click; False if it failed and the page needs a reload."""
        clicked = time.time()
        counted = self.report.in_window
        try:
            result = await self.act(scenario)
        except Exception as err:  # pylint: disable=broad-except
            if counted(clicked):
                kind = (
                    "timeout"
                    if isinstance(err, asyncio.TimeoutError)
                    else type(err).__name__
                )
                self.report.error(f"{scenario}:{kind}")
            return False
        if counted(clicked):
            self.report.counts["actions"] += 1
            if scenario == "stream":
                self.report.add("stream_first", result["first"])
                self.report.add("stream_total", result["total"])
            else:
                self.report.add(scenario, result["total"])
        return True

    async def run(self, start_at, stop_at):
        await asyncio.sleep(max(0.0, start_at - time.time()))
        context = await self._start()
        if context is None:
            return
        loaded = True
        try:
            while time.time() < stop_at:
                if not loaded and not await self._reload():
                    continue
                # Not a security use: just varies what users click.
                scenario = random.choice(self.args.scenario)  # NOSONAR
                loaded = await self._click(scenario)
                await asyncio.sleep(random.uniform(0, 2 * self.args.think))  # NOSONAR
        finally:
            with contextlib.suppress(Exception):
                await context.close()


async def _watch_cpu(report, stop_at, samples):
    """Sample this machine's CPU (browsers included) inside the window."""
    psutil.cpu_percent(None)
    while time.time() < stop_at:
        await asyncio.sleep(2)
        if report.in_window(time.time()):
            samples.append(psutil.cpu_percent(None))
        else:
            psutil.cpu_percent(None)


async def main(args):
    start = args.start_at or time.time() + 5
    measure_from = start + args.ramp
    stop_at = measure_from + args.duration
    report = Report(measure_from, stop_at)
    cpu = []
    async with async_playwright() as pw:
        browsers = await asyncio.gather(
            *(
                pw.chromium.launch(
                    headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"]
                )
                for _ in range(args.browsers)
            )
        )
        # Past the shared start, this agent's ramp is compressed and the swarm
        # no longer starts together; the report says by how much.
        late = max(0.0, time.time() - start)
        users = [
            User(browsers[i % len(browsers)], args, report) for i in range(args.users)
        ]
        watcher = asyncio.ensure_future(_watch_cpu(report, stop_at, cpu))
        await asyncio.gather(
            *(
                u.run(start + args.ramp * i / max(1, args.users), stop_at)
                for i, u in enumerate(users)
            )
        )
        watcher.cancel()
        for browser in browsers:
            with contextlib.suppress(Exception):
                await browser.close()

    cpu.sort()
    out = {
        "agent": args.agent_id or socket.gethostname(),
        "target": args.target,
        "users": args.users,
        "browsers": args.browsers,
        "scenario": args.scenario,
        "think": args.think,
        "window": [measure_from, stop_at],
        "duration": args.duration,
        "late_s": round(late, 2),
        "cpus": psutil.cpu_count(),
        "cpu_mean_pct": round(sum(cpu) / len(cpu)) if cpu else None,
        # p90 of 2 s samples: one spike shouldn't flag an agent as bound.
        "cpu_p90_pct": round(cpu[int(0.9 * (len(cpu) - 1))]) if cpu else None,
        **report.counts,
        "errors_by_kind": report.errors_by_kind,
        "histograms": {k: h.to_json() for k, h in report.hists.items()},
    }
    return out


def write_report(out, path):
    text = json.dumps(out)
    if path == "-":
        print(text)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    summary = {
        k: Histogram.from_json(h).summary() for k, h in out["histograms"].items()
    }
    print(
        json.dumps(
            {
                "agent": out["agent"],
                "actions": out["actions"],
                "errors": out["errors"],
                "late_s": out["late_s"],
                "cpu_p90_pct": out["cpu_p90_pct"],
                **summary,
            }
        ),
        file=sys.stderr,
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--target", required=True, help="the app's URL")
    parser.add_argument("--users", type=int, default=20)
    parser.add_argument(
        "--browsers",
        type=int,
        help="Chromium processes the users share (default: one per 10 users)",
    )
    parser.add_argument(
        "--scenario",
        default="http,ws,stream",
        type=lambda s: [x for x in s.split(",") if x],
    )
    parser.add_argument("--think", type=float, default=1.0)
    parser.add_argument(
        "--start-at",
        type=float,
        help="wall-clock start shared by the swarm (default: in 5 s)",
    )
    parser.add_argument("--ramp", type=float, default=30.0)
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--agent-id")
    parser.add_argument("--out", default="-")
    args = parser.parse_args(argv)
    if args.browsers is None:
        args.browsers = max(1, math.ceil(args.users / 10))
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    write_report(asyncio.run(main(ARGS)), ARGS.out)
