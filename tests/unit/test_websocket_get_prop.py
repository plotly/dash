"""Partial-read get_prop protocol tests without a browser or server."""

import asyncio
import json
import threading
from contextlib import asynccontextmanager

import janus
import pytest

from dash.backends.ws import (
    _JS_MAX_SAFE_INTEGER,
    DashWebsocketCallback,
    _validate_prop_path,
)


@asynccontextmanager
async def websocket(threaded=False):
    outbound = janus.Queue()
    pending = {}
    ws = DashWebsocketCallback(
        pending,
        "renderer",
        outbound,
        threading.Event(),
        None if threaded else asyncio.get_running_loop(),
    )
    try:
        yield ws, pending, outbound
    finally:
        outbound.close()
        await outbound.wait_closed()


def start_read(ws, threaded, *args, **kwargs):
    read = ws.get_prop(*args, **kwargs)
    if threaded:
        read = asyncio.to_thread(asyncio.run, read)
    return asyncio.create_task(read)


async def next_request(outbound):
    return json.loads(await asyncio.wait_for(outbound.async_q.get(), timeout=2))


def respond(pending, message, payload):
    waiter = pending[message["requestId"]]
    if isinstance(waiter, asyncio.Future):
        waiter.set_result(payload)
    else:
        waiter.put_nowait(payload)


@pytest.mark.parametrize(
    "path",
    [
        None,
        [],
        ["records", 0, -1],
        [_JS_MAX_SAFE_INTEGER],
        [-_JS_MAX_SAFE_INTEGER],
    ],
)
def test_validate_prop_path_accepts_supported_values(path):
    _validate_prop_path(path)


@pytest.mark.parametrize("threaded", [False, True])
@pytest.mark.parametrize(
    "options", [{}, {"path": None}, {"path": []}, {"path": ["a", -1, 0]}]
)
def test_get_prop_request(threaded, options):
    async def run():
        async with websocket(threaded) as (ws, pending, outbound):
            # The third positional argument remains the timeout.
            task = start_read(ws, threaded, "store", "data", 2.0, **options)
            message = await next_request(outbound)
            payload = {"componentId": "store", "properties": ["data"]}
            if options.get("path") is not None:
                payload["path"] = options["path"]
            assert message == {
                "type": "get_props_request",
                "rendererId": "renderer",
                "requestId": message["requestId"],
                "payload": payload,
            }
            respond(pending, message, {"data": 42})
            assert await asyncio.wait_for(task, 2) == 42
            assert not pending

    asyncio.run(run())


@pytest.mark.parametrize("threaded", [False, True])
@pytest.mark.parametrize("value", [0, False, "", [], {}, None])
def test_get_prop_preserves_json_values(threaded, value):
    async def run():
        async with websocket(threaded) as (ws, pending, outbound):
            task = start_read(ws, threaded, "store", "data", path=["selected"])
            message = await next_request(outbound)
            respond(pending, message, {"data": value})
            result = await asyncio.wait_for(task, 2)
            assert result == value
            assert type(result) is type(value)
            assert not pending

    asyncio.run(run())


@pytest.mark.parametrize(
    "path",
    [
        "a.b",
        ("a",),
        {},
        0,
        True,
        [True],
        [1.0],
        [None],
        [[]],
        [slice(1)],
        ["a", {}],
    ],
)
def test_get_prop_invalid_path(path):
    async def run():
        async with websocket() as (ws, pending, outbound):
            with pytest.raises(TypeError, match="path"):
                await ws.get_prop("store", "data", path=path)
            assert not pending
            assert outbound.sync_q.empty()

    asyncio.run(run())


@pytest.mark.parametrize("index", [2**53, -(2**53)])
def test_get_prop_unsafe_index(index):
    async def run():
        async with websocket() as (ws, pending, outbound):
            with pytest.raises(ValueError, match="safe integer"):
                await ws.get_prop("store", "data", path=["a", index])
            assert not pending
            assert outbound.sync_q.empty()

    asyncio.run(run())


def test_get_prop_path_is_keyword_only():
    async def run():
        async with websocket() as (ws, pending, outbound):
            with pytest.raises(TypeError):
                await ws.get_prop("store", "data", 2.0, ["a"])
            assert not pending
            assert outbound.sync_q.empty()

    asyncio.run(run())


@pytest.mark.parametrize("threaded", [False, True])
def test_get_prop_path_preserves_timeout_cleanup(threaded):
    async def run():
        async with websocket(threaded) as (ws, pending, outbound):
            task = start_read(ws, threaded, "store", "data", timeout=0.05, path=[0])
            message = await next_request(outbound)
            with pytest.raises(TimeoutError, match="store.data"):
                await asyncio.wait_for(task, 2)
            assert message["requestId"] not in pending

    asyncio.run(run())
