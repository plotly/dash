"""The stream hub: streaming frames multiplexed over shared-storage pub/sub."""
import asyncio
import threading
import time
import uuid

import pytest

from dash._shared_storage import LocalSharedStorage
from dash._streaming import StreamedCallbackResponse
from dash._stream_hub import (
    apump_to_storage,
    publish_frame,
    pump_to_storage,
    stream_topic,
    subscribe_envelopes,
)


def _frames_marker(*frames):
    async def gen():
        for frame in frames:
            yield frame

    return StreamedCallbackResponse(gen(), is_async=True)


@pytest.fixture
def storage():
    s = LocalSharedStorage(namespace=f"hub-{uuid.uuid4().hex[:12]}")
    s.start()
    yield s
    s.close()


def _drain(storage, conn_id, stop_after, out, replay_from=None):
    gen = subscribe_envelopes(storage, conn_id, replay_from)
    for envelope in gen:
        out.append(envelope)
        if len(out) >= stop_after:
            break
    gen.close()


def test_topic_name():
    assert stream_topic("abc") == "_dash_stream:abc"


def test_downlink_relays_tagged_frames(storage):
    out = []
    th = threading.Thread(target=_drain, args=(storage, "c1", 2, out))
    th.start()
    time.sleep(0.3)  # let the subscription establish (pub/sub starts at head)

    publish_frame(
        storage, "c1", "r1", {"multi": True, "response": {"o": {"children": "a"}}}
    )
    publish_frame(storage, "c1", "r1", {"done": True})

    th.join(timeout=5)
    assert [(e["rid"], e["frame"]) for e in out] == [
        ("r1", {"multi": True, "response": {"o": {"children": "a"}}}),
        ("r1", {"done": True}),
    ]
    # Each envelope carries its storage seq, ascending, for reconnect resume.
    assert [e["seq"] for e in out] == [1, 2]


def test_downlink_multiplexes_multiple_callbacks(storage):
    out = []
    th = threading.Thread(target=_drain, args=(storage, "c2", 4, out))
    th.start()
    time.sleep(0.3)

    # Two callbacks' frames interleave on one connection; the client demuxes by rid.
    publish_frame(storage, "c2", "r1", {"response": {"a": 1}})
    publish_frame(storage, "c2", "r2", {"response": {"b": 1}})
    publish_frame(storage, "c2", "r1", {"done": True})
    publish_frame(storage, "c2", "r2", {"done": True})

    th.join(timeout=5)
    rids = [e["rid"] for e in out]
    assert rids == ["r1", "r2", "r1", "r2"]


def test_reconnecting_downlink_replays_from_cursor(storage):
    topic = stream_topic("c3")
    # Publish before anyone subscribes; a reconnecting downlink replays from 0.
    publish_frame(storage, "c3", "r1", {"response": {"a": 1}})
    publish_frame(storage, "c3", "r1", {"done": True})

    out = []
    _drain(storage, "c3", 2, out, replay_from=0)
    assert [e["frame"] for e in out] == [{"response": {"a": 1}}, {"done": True}]
    assert storage.get(topic) is None  # topics are pub/sub, not KV keys


def test_async_pump_publishes_frames(storage):
    marker = _frames_marker({"response": {"a": 1}}, {"done": True})
    out = []
    th = threading.Thread(target=_drain, args=(storage, "cp", 2, out))
    th.start()
    time.sleep(0.3)
    asyncio.run(apump_to_storage(storage, "cp", "r9", marker))
    th.join(timeout=5)
    assert [(e["rid"], e["frame"]) for e in out] == [
        ("r9", {"response": {"a": 1}}),
        ("r9", {"done": True}),
    ]


def test_publish_frame_reduces_patch_to_plain_json(storage):
    # A frame carrying a dash.Patch must be reduced to plain JSON before it hits
    # shared storage, or the data-only wire codec (msgspec) cannot encode it --
    # the failure seen in multi-process deployments (the socket path).
    from dash import Patch
    from dash._shared_storage._codec import encode

    patch = Patch()
    patch["x"] = 1
    frame = {"multi": True, "response": {"o": {"children": patch}}}

    out = []
    th = threading.Thread(target=_drain, args=(storage, "cpatch", 1, out), daemon=True)
    th.start()
    time.sleep(0.3)
    publish_frame(storage, "cpatch", "r1", frame)
    th.join(timeout=5)

    delivered = out[0]["frame"]
    encode(delivered)  # the op that raised over the socket; must not raise now
    child = delivered["response"]["o"]["children"]
    assert child["__dash_patch_update"] == "__dash_patch_update"


def test_sync_pump_drives_async_frames(storage):
    marker = _frames_marker({"response": {"b": 2}}, {"done": True})
    out = []
    th = threading.Thread(target=_drain, args=(storage, "cs", 2, out))
    th.start()
    time.sleep(0.3)
    pump_to_storage(storage, "cs", "r10", marker)  # sync driver over async gen
    th.join(timeout=5)
    assert [e["frame"] for e in out] == [{"response": {"b": 2}}, {"done": True}]
