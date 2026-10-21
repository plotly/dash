"""Simulated browsers for the streaming load test.

Run by ``benchmarks.streaming.load``, several processes at once: one Python
process saturates its own CPU at a few hundred browsers and then reports its
own slowness as server latency.

Each browser loads the page once (for its signed ``end_id`` and the server's
stream mode), then loops: click (uplink POST), read its frames off the
downlink until the ``done`` frame, think, click again. The downlink follows
the renderer's ``StreamClient``: one long NDJSON response in ``stream`` mode
(ASGI), or polling with the same pacing and backoff in ``poll`` mode (WSGI).

Prints one JSON line with the measurements of every stream clicked inside the
measure window, however late it finished: counting by finish time would drop
exactly the slow streams a struggling server produces.
"""
import argparse
import asyncio
import json
import random
import re
import sys
import time

import aiohttp

CONFIG_RE = re.compile(r'<script id="_dash-config"[^>]*>(.*?)</script>', re.S)
STAMP_RE = re.compile(r'"(\d{10}\.\d{6})"')
UPDATE = "/_dash-update-component"
# Matches streamClient.ts.
EMPTY_POLLS_BEFORE_BACKOFF = 2
MAX_BACKOFF_FACTOR = 5

CLICK = {
    "output": "out.children",
    "outputs": {"id": "out", "property": "children"},
    "inputs": [{"id": "btn", "property": "n_clicks", "value": 1}],
    "changedPropIds": ["btn.n_clicks"],
    "state": [],
}


class StreamReset(Exception):
    pass


class Stats:
    def __init__(self, measure_from, measure_to):
        self.measure_from = measure_from
        self.measure_to = measure_to
        self.latency_ms = []
        self.first_frame_ms = []
        self.streams = 0
        self.frames = 0
        self.errors = 0
        self.incomplete = 0
        self.failed_browsers = 0

    def in_window(self, t):
        return self.measure_from <= t <= self.measure_to


async def _lines(resp):
    buf = b""
    async for chunk in resp.content.iter_any():
        buf += chunk
        *lines, buf = buf.split(b"\n")
        for line in lines:
            if line.strip():
                yield json.loads(line)
    if buf.strip():
        yield json.loads(buf)


class Browser:
    def __init__(self, base, stats, frames, think):
        self.base = base
        self.stats = stats
        self.expected = frames
        self.think = think
        self.cursor = 0
        # Set from the page config by load_page().
        self.end_id = ""
        self.mode = "stream"
        self.poll_interval = 0.1
        # Browsers cap connections per host at six.
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=6),
            timeout=aiohttp.ClientTimeout(total=None, sock_connect=30),
        )

    async def load_page(self):
        async with self.session.get(self.base + "/") as resp:
            text = await resp.text()
        config = json.loads(CONFIG_RE.search(text).group(1))
        stream = config.get("stream") or {}
        self.end_id = config["end_id"]
        self.mode = stream.get("mode", "stream")
        self.poll_interval = stream.get("poll_interval", 100) / 1000

    def _url(self):
        return f"{self.base}{UPDATE}?endId={self.end_id}"

    def _frame(self, frame, clicked, state):
        now = time.time()
        if frame.get("done"):
            return True
        match = STAMP_RE.search(json.dumps(frame))
        if match:
            counted = self.stats.in_window(clicked)
            if state["frames"] == 0 and counted:
                self.stats.first_frame_ms.append((now - clicked) * 1000)
            state["frames"] += 1
            if counted:
                self.stats.latency_ms.append((now - float(match.group(1))) * 1000)
                self.stats.frames += 1
        return False

    def _envelopes(self, envelope, rid, clicked, state):
        if envelope.get("reset"):
            # The renderer settles every pending stream on a reset.
            self.cursor = 0
            raise StreamReset()
        if isinstance(envelope.get("seq"), int):
            self.cursor = envelope["seq"]
        if envelope.get("rid") != rid:
            return False
        return self._frame(envelope.get("frame") or {}, clicked, state)

    async def _downlink_stream(self, rid, clicked, state):
        # Like the renderer, reconnect from the cursor if the downlink closes
        # before the done frame, backing off when it closed with nothing.
        while True:
            got = False
            async with self.session.post(
                self._url(), json={"streamDownlink": {"from": self.cursor}}
            ) as resp:
                resp.raise_for_status()
                async for envelope in _lines(resp):
                    got = True
                    if self._envelopes(envelope, rid, clicked, state):
                        return
            if not got:
                await asyncio.sleep(1)

    async def _downlink_poll(self, rid, clicked, state):
        empty = 0
        while True:
            async with self.session.post(
                self._url(), json={"streamDownlink": {"from": self.cursor}}
            ) as resp:
                resp.raise_for_status()
                envelopes = [e async for e in _lines(resp)]
            for envelope in envelopes:
                if self._envelopes(envelope, rid, clicked, state):
                    return
            empty = 0 if envelopes else empty + 1
            factor = 1
            if empty > EMPTY_POLLS_BEFORE_BACKOFF:
                factor = min(
                    2 ** (empty - EMPTY_POLLS_BEFORE_BACKOFF), MAX_BACKOFF_FACTOR
                )
            await asyncio.sleep(self.poll_interval * factor)

    async def one_stream(self, n):
        rid = f"{id(self)}-{n}"
        clicked = time.time()
        async with self.session.post(
            self._url(), json={**CLICK, "streamConnection": {"requestId": rid}}
        ) as resp:
            resp.raise_for_status()
            await resp.read()
        state = {"frames": 0}
        if self.mode == "poll":
            await self._downlink_poll(rid, clicked, state)
        else:
            await self._downlink_stream(rid, clicked, state)
        if self.stats.in_window(clicked):
            self.stats.streams += 1
            if state["frames"] < self.expected:
                self.stats.incomplete += 1

    async def run(self, start_at, stop_at):
        await asyncio.sleep(max(0.0, start_at - time.time()))
        n = 0
        try:
            await asyncio.wait_for(self.load_page(), timeout=30)
            while time.time() < stop_at:
                n += 1
                clicked = time.time()
                try:
                    await asyncio.wait_for(self.one_stream(n), timeout=60)
                except (
                    aiohttp.ClientError,
                    asyncio.TimeoutError,
                    ValueError,
                    StreamReset,
                ):
                    if self.stats.in_window(clicked):
                        self.stats.errors += 1
                    await asyncio.sleep(1)
                await asyncio.sleep(random.uniform(0, 2 * self.think))
        except (aiohttp.ClientError, asyncio.TimeoutError, AttributeError, ValueError):
            # The page never loaded: this browser never got to stream at all.
            self.stats.errors += 1
            self.stats.failed_browsers += 1
        finally:
            await self.session.close()


async def main(args):
    start = args.start
    ramp_end = start + args.ramp
    stats = Stats(ramp_end, ramp_end + args.duration)
    browsers = [
        Browser(args.url, stats, args.frames, args.think) for _ in range(args.browsers)
    ]
    await asyncio.gather(
        *(
            b.run(start + args.ramp * i / max(1, args.browsers), stats.measure_to)
            for i, b in enumerate(browsers)
        )
    )
    json.dump(
        {
            "latency_ms": [round(x, 2) for x in stats.latency_ms],
            "first_frame_ms": [round(x, 2) for x in stats.first_frame_ms],
            "streams": stats.streams,
            "frames": stats.frames,
            "errors": stats.errors,
            "incomplete": stats.incomplete,
            "failed_browsers": stats.failed_browsers,
        },
        sys.stdout,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--browsers", type=int, required=True)
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--think", type=float, default=1.0)
    parser.add_argument("--start", type=float, required=True)
    parser.add_argument("--ramp", type=float, default=5.0)
    parser.add_argument("--duration", type=float, default=20.0)
    asyncio.run(main(parser.parse_args()))
