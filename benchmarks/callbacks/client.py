"""Simulated browsers for the callback load test.

Run by ``benchmarks.callbacks.load``, several processes at once. Each browser
loads the page once, then loops: click, wait for the callback's response,
think, click again. Over ``http`` every click is a POST to
``/_dash-update-component``, as the renderer sends it (six connections per
host at most, kept alive). Over ``ws`` the browser holds one websocket to
``/_dash-ws-callback`` and sends ``callback_request`` messages on it, as the
renderer's SharedWorker does; replies may arrive batched in a JSON array.

Prints one JSON line with the round trip of every click made inside the
measure window, however late it finished.
"""
import argparse
import asyncio
import itertools
import json
import random
import sys
import time

import aiohttp

UPDATE = "/_dash-update-component"
WS = "/_dash-ws-callback"
TIMEOUT = 30


def _payload(n):
    return {
        "output": "out.children",
        "outputs": {"id": "out", "property": "children"},
        "inputs": [{"id": "btn", "property": "n_clicks", "value": n}],
        "changedPropIds": ["btn.n_clicks"],
        "state": [],
    }


class Stats:
    def __init__(self, measure_from, measure_to):
        self.measure_from = measure_from
        self.measure_to = measure_to
        self.rtt_ms = []
        self.calls = 0
        self.errors = 0
        self.failed_browsers = 0

    def in_window(self, t):
        return self.measure_from <= t <= self.measure_to


class Browser:
    _ids = itertools.count()

    def __init__(self, base, stats, transport, think):
        self.base = base
        self.stats = stats
        self.transport = transport
        self.think = think
        self.renderer_id = f"r{next(self._ids)}"
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=6),
            timeout=aiohttp.ClientTimeout(total=None, sock_connect=30),
        )
        self.ws = None
        self.pending = {}
        self.readers = set()

    async def _http_call(self, n):
        async with self.session.post(self.base + UPDATE, json=_payload(n)) as resp:
            resp.raise_for_status()
            body = await resp.json(content_type=None)
        if "response" not in body:
            raise ValueError(f"unexpected response {body!r:.200}")

    async def _ws_connect(self):
        self.ws = await self.session.ws_connect(
            self.base.replace("http", "ws", 1) + WS,
            origin=self.base,
            max_msg_size=0,
        )
        # Each connection gets its own pending requests: a closing one must
        # not fail the requests of the connection that replaced it.
        self.pending = {}
        self.readers.add(asyncio.ensure_future(self._ws_read(self.ws, self.pending)))

    @staticmethod
    async def _ws_read(ws, pending):
        try:
            async for msg in ws:
                if msg.type != aiohttp.WSMsgType.TEXT:
                    break
                data = json.loads(msg.data)
                for item in data if isinstance(data, list) else [data]:
                    if item.get("type") == "callback_response":
                        fut = pending.pop(item.get("requestId"), None)
                        if fut is not None and not fut.done():
                            fut.set_result(item.get("payload"))
        finally:
            for fut in pending.values():
                if not fut.done():
                    fut.set_exception(ConnectionError("websocket closed"))
            pending.clear()

    async def _ws_call(self, n):
        request_id = f"{self.renderer_id}-{n}"
        fut = asyncio.get_running_loop().create_future()
        self.pending[request_id] = fut
        await self.ws.send_json(
            {
                "type": "callback_request",
                "requestId": request_id,
                "rendererId": self.renderer_id,
                "payload": _payload(n),
            }
        )
        payload = await fut
        if not isinstance(payload, dict) or payload.get("status") == "error":
            raise ValueError(f"unexpected response {payload!r:.200}")

    async def run(self, start_at, stop_at):
        await asyncio.sleep(max(0.0, start_at - time.time()))
        call = self._ws_call if self.transport == "ws" else self._http_call
        try:
            async with self.session.get(self.base + "/") as resp:
                resp.raise_for_status()
                await resp.read()
            n = 0
            while time.time() < stop_at:
                n += 1
                if self.transport == "ws" and (self.ws is None or self.ws.closed):
                    # Connecting is not part of a click's round trip; the
                    # renderer connects once and reuses the socket.
                    try:
                        await asyncio.wait_for(self._ws_connect(), timeout=TIMEOUT)
                    except (aiohttp.ClientError, asyncio.TimeoutError):
                        if self.stats.in_window(time.time()):
                            self.stats.errors += 1
                        await asyncio.sleep(1)
                        continue
                clicked = time.time()
                try:
                    await asyncio.wait_for(call(n), timeout=TIMEOUT)
                    if self.stats.in_window(clicked):
                        self.stats.calls += 1
                        self.stats.rtt_ms.append((time.time() - clicked) * 1000)
                except (
                    aiohttp.ClientError,
                    asyncio.TimeoutError,
                    ConnectionError,
                    ValueError,
                ):
                    if self.stats.in_window(clicked):
                        self.stats.errors += 1
                    if self.ws is not None:
                        await self.ws.close()
                    await asyncio.sleep(1)
                await asyncio.sleep(random.uniform(0, 2 * self.think))
        except (aiohttp.ClientError, asyncio.TimeoutError):
            # The page never loaded: this browser never got to click at all.
            self.stats.errors += 1
            self.stats.failed_browsers += 1
        finally:
            if self.ws is not None:
                await self.ws.close()
            for reader in self.readers:
                reader.cancel()
            await self.session.close()


async def main(args):
    stats = Stats(args.start + args.ramp, args.start + args.ramp + args.duration)
    browsers = [
        Browser(args.url, stats, args.transport, args.think)
        for _ in range(args.browsers)
    ]
    await asyncio.gather(
        *(
            b.run(args.start + args.ramp * i / max(1, args.browsers), stats.measure_to)
            for i, b in enumerate(browsers)
        )
    )
    json.dump(
        {
            "rtt_ms": [round(x, 2) for x in stats.rtt_ms],
            "calls": stats.calls,
            "errors": stats.errors,
            "failed_browsers": stats.failed_browsers,
        },
        sys.stdout,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--browsers", type=int, required=True)
    parser.add_argument("--transport", choices=["http", "ws"], default="http")
    parser.add_argument("--think", type=float, default=1.0)
    parser.add_argument("--start", type=float, required=True)
    parser.add_argument("--ramp", type=float, default=5.0)
    parser.add_argument("--duration", type=float, default=20.0)
    asyncio.run(main(parser.parse_args()))
