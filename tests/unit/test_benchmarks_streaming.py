"""Multi-worker streaming setups run on local shared storage, never skipped."""
import asyncio
import json
from types import SimpleNamespace

import pytest

from benchmarks import loadkit
from benchmarks.streaming import load


def test_every_setup_runs_without_redis(tmp_path):
    args = SimpleNamespace(browsers=[10], out=str(tmp_path / "results.json"))
    results = {"setups": []}

    def run_point(_setup, browsers, _args):
        return {
            "browsers": browsers,
            "saturated": False,
            "client_bound": False,
            "client_cpu_peak_pct": 0,
            "server_cpu_cores": 0,
            "error_rate": 0,
        }

    loadkit.sweep(
        results, load.SETUPS, args, run_point, lambda _p: "", load._entry_fields
    )

    ran = {s["name"]: s for s in results["setups"]}
    assert set(ran) == {s.name for s in load.SETUPS}
    assert any(s.workers > 1 for s in load.SETUPS)
    assert all(s["storage"] == "local" for s in ran.values())


def test_each_click_reads_a_fresh_downlink_from_its_start():
    # Installed for the load tests, not by the unit test requirements.
    pytest.importorskip("aiohttp")
    asyncio.run(_two_clicks())


async def _two_clicks():
    # pylint: disable-next=import-outside-toplevel
    from aiohttp import web

    # pylint: disable-next=import-outside-toplevel
    from benchmarks.streaming import client

    seen = []
    rid = {}

    async def update(request):
        body = await request.json()
        seen.append(
            (
                request.query.get("downlinkId"),
                "streamDownlink" in body,
                (body.get("streamDownlink") or {}).get("from"),
            )
        )
        if "streamConnection" in body:
            rid["last"] = body["streamConnection"]["requestId"]
            return web.Response(text="{}")
        envelope = {"seq": 9, "rid": rid["last"], "frame": {"done": True}}
        return web.Response(text=json.dumps(envelope) + "\n")

    app = web.Application()
    app.router.add_post("/_dash-update-component", update)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]  # pylint: disable=protected-access
    try:
        browser = client.Browser(
            f"http://127.0.0.1:{port}", client.Stats(0, 1e12), frames=0, think=0
        )
        browser.end_id = "end"
        try:
            await browser.one_stream(1)
            await browser.one_stream(2)
        finally:
            await browser.session.close()
    finally:
        await runner.cleanup()

    first, second = seen[:2], seen[2:]
    assert first[0][0] and first[0][0] == first[1][0]
    assert second[0][0] and second[0][0] == second[1][0]
    assert first[0][0] != second[0][0]
    assert first[1][2] == 0 and second[1][2] == 0
