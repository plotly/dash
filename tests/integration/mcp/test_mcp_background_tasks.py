"""Background callback support through the MCP HTTP endpoint.

End-to-end flows: trigger a background callback, poll via
``get_background_task_result``, observe progress (``set_progress``),
confirm the cache-expiry behavior, and verify the background-only tools
appear in ``tools/list``.
"""

import json
import re
import subprocess
import sys
import time

import diskcache
import psutil
from dash import Dash, Input, Output, html, _callback_signing
from dash.background_callback.managers.diskcache_manager import DiskcacheManager

MCP_PATH = "_mcp"


def _unwrap_handles(app, task_id):
    """Return the raw (unsigned) ``(job_id, cache_key)`` from a signed taskId.

    The handles embedded in a taskId are HMAC-signed (see ``_callback_signing``);
    tests that poke the manager directly must unwrap them first. MCP dispatch has
    no end_id, so the ``None`` end_id scope is used.
    """
    secret = app._get_signing_secret()
    _tool, signed_job, rest = task_id.split(":", 2)
    signed_cache, _epoch = rest.rsplit(":", 1)
    job_id = _callback_signing.unsign(
        secret, _callback_signing.job_scope(None), signed_job
    )
    cache_key = _callback_signing.unsign(
        secret, _callback_signing.cache_scope(None), signed_cache
    )
    return job_id, cache_key


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_background_app():
    cache = diskcache.Cache()
    manager = DiskcacheManager(cache)

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="input"),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("input", "children"),
        background=True,
        manager=manager,
    )
    def slow_callback(value):
        time.sleep(0.5)
        return f"done: {value}"

    return app


def _post(client, method, params=None, request_id=1):
    return client.post(
        f"/{MCP_PATH}",
        data=json.dumps(
            {
                "jsonrpc": "2.0",
                "method": method,
                "id": request_id,
                "params": params or {},
            }
        ),
        headers={"Content-Type": "application/json"},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_mcpbg012_trigger_poll_and_retrieve():
    app = _make_background_app()
    client = app.server.test_client()

    # Trigger
    r = _post(
        client,
        "tools/call",
        {"name": "slow_callback", "arguments": {"value": "hello"}},
    )
    assert r.status_code == 200
    data = json.loads(r.data)
    task_info = json.loads(data["result"]["content"][0]["text"])
    task_id = task_info["taskId"]
    assert task_info["status"] == "working"

    # Poll — should be working
    r = _post(
        client,
        "tools/call",
        {
            "name": "get_background_task_result",
            "arguments": {"taskId": task_id},
        },
        request_id=2,
    )
    assert r.status_code == 200
    poll_data = json.loads(json.loads(r.data)["result"]["content"][0]["text"])
    assert poll_data["status"] == "working"

    # Wait for completion
    job_id, _ = _unwrap_handles(app, task_id)
    manager = app.callback_map["output.children"]["manager"]
    deadline = time.time() + 5
    while time.time() < deadline:
        if not manager.job_running(job_id):
            break
        time.sleep(0.1)

    # Get result
    r = _post(
        client,
        "tools/call",
        {
            "name": "get_background_task_result",
            "arguments": {"taskId": task_id},
        },
        request_id=3,
    )
    assert r.status_code == 200
    data = json.loads(r.data)
    text = data["result"]["content"][0]["text"]
    assert "done:" in text


def test_mcpbg013_result_expires():
    """Result is retrievable until the cache expires, then reports failure."""
    cache = diskcache.Cache()
    manager = DiskcacheManager(cache, cache_by=[lambda: "fixed"], expire=2)

    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="input"), html.Div(id="output")])

    @app.callback(
        Output("output", "children"),
        Input("input", "children"),
        background=True,
        manager=manager,
    )
    def fast_cb(value):
        return f"done: {value}"

    client = app.server.test_client()

    r = _post(
        client,
        "tools/call",
        {"name": "fast_cb", "arguments": {"value": "hi"}},
    )
    task_info = json.loads(json.loads(r.data)["result"]["content"][0]["text"])
    task_id = task_info["taskId"]
    job_id, _ = _unwrap_handles(app, task_id)

    deadline = time.time() + 3
    while time.time() < deadline:
        if not manager.job_running(job_id):
            break
        time.sleep(0.1)

    # Before expiry — result available
    r = _post(
        client,
        "tools/call",
        {
            "name": "get_background_task_result",
            "arguments": {"taskId": task_id},
        },
        request_id=2,
    )
    assert "done:" in json.loads(r.data)["result"]["content"][0]["text"]

    time.sleep(2.5)

    # After expiry — tool reports failure
    r = _post(
        client,
        "tools/call",
        {
            "name": "get_background_task_result",
            "arguments": {"taskId": task_id},
        },
        request_id=3,
    )
    poll_data = json.loads(json.loads(r.data)["result"]["content"][0]["text"])
    assert poll_data["status"] == "failed"


def test_mcpbg014_progress_in_poll_response():
    """Progress reported via set_progress appears in poll statusMessage."""
    cache = diskcache.Cache()
    manager = DiskcacheManager(cache)

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="input"),
            html.Div(id="status"),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("input", "children"),
        progress=Output("status", "children"),
        background=True,
        manager=manager,
        interval=200,
    )
    def progress_cb(set_progress, value):
        for i in range(10):
            set_progress(f"Step {i + 1} of 10")
            time.sleep(0.2)
        return f"done: {value}"

    client = app.server.test_client()

    # Trigger
    r = _post(
        client,
        "tools/call",
        {"name": "progress_cb", "arguments": {"value": "hi"}},
    )
    task_info = json.loads(json.loads(r.data)["result"]["content"][0]["text"])
    task_id = task_info["taskId"]

    # Poll and collect all progress messages
    progress_pattern = re.compile(r"Step \d+ of 10")
    progress_messages = []
    deadline = time.time() + 10
    while time.time() < deadline:
        r = _post(
            client,
            "tools/call",
            {
                "name": "get_background_task_result",
                "arguments": {"taskId": task_id},
            },
            request_id=2,
        )
        text = json.loads(r.data)["result"]["content"][0]["text"]
        try:
            poll_data = json.loads(text)
            msg = poll_data.get("statusMessage")
            if msg is not None:
                progress_messages.append(msg)
            if poll_data.get("status") == "completed":
                break
        except (json.JSONDecodeError, KeyError):
            break
        time.sleep(0.3)

    assert len(progress_messages) > 0, "Expected progress updates during polling"
    for msg in progress_messages:
        assert progress_pattern.search(msg), f"Unexpected progress format: {msg}"


def test_mcpbg015_background_tools_in_tools_list():
    app = _make_background_app()
    client = app.server.test_client()
    r = _post(client, "tools/list")
    data = json.loads(r.data)
    names = [t["name"] for t in data["result"]["tools"]]
    assert "get_background_task_result" in names
    assert "cancel_background_task" in names
    assert "slow_callback" in names


def test_mcpbg016_per_callback_manager_lookup():
    """``tasks/get`` uses the manager attached to the specific callback."""
    manager_a = DiskcacheManager(diskcache.Cache())
    manager_b = DiskcacheManager(diskcache.Cache())

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="input_a"),
            html.Div(id="output_a"),
            html.Div(id="input_b"),
            html.Div(id="output_b"),
        ]
    )

    @app.callback(
        Output("output_a", "children"),
        Input("input_a", "children"),
        background=True,
        manager=manager_a,
    )
    def callback_a(value):
        time.sleep(0.5)
        return f"a: {value}"

    @app.callback(
        Output("output_b", "children"),
        Input("input_b", "children"),
        background=True,
        manager=manager_b,
    )
    def callback_b(value):
        time.sleep(0.5)
        return f"b: {value}"

    client = app.server.test_client()

    r = _post(
        client,
        "tools/call",
        {"name": "callback_b", "arguments": {"value": "hello"}},
    )
    assert r.status_code == 200
    task_info = json.loads(json.loads(r.data)["result"]["content"][0]["text"])
    task_id = task_info["taskId"]
    _, cache_key = _unwrap_handles(app, task_id)

    deadline = time.time() + 5
    while time.time() < deadline:
        if manager_b.result_ready(cache_key):
            break
        time.sleep(0.1)

    assert manager_b.result_ready(cache_key)
    assert not manager_a.result_ready(cache_key)

    r = _post(client, "tasks/get", {"taskId": task_id}, request_id=2)
    assert r.status_code == 200
    assert json.loads(r.data)["result"]["status"] == "completed"


# ---------------------------------------------------------------------------
# Security: taskId handles are signed and verified end-to-end
# ---------------------------------------------------------------------------


def test_mcpbg017_forged_cancel_does_not_kill_arbitrary_process():
    """A crafted taskId with an arbitrary pid must not reach terminate_job."""
    app = _make_background_app()
    client = app.server.test_client()

    victim = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        time.sleep(0.2)
        assert psutil.pid_exists(victim.pid)

        # Unsigned taskId an attacker would craft: <tool>:<victim_pid>:<key>:<epoch>
        forged = f"slow_callback:{victim.pid}:deadbeef:0"
        r = _post(client, "tasks/cancel", {"taskId": forged})

        # The malformed/forged handle is rejected as a JSON-RPC error, and the
        # unrelated process is left untouched.
        body = json.loads(r.data)
        assert "error" in body or body.get("result", {}).get("status") != "cancelled"
        time.sleep(0.3)
        assert psutil.pid_exists(victim.pid)
        assert psutil.Process(victim.pid).status() != psutil.STATUS_ZOMBIE
    finally:
        victim.kill()


def test_mcpbg018_forged_result_does_not_read_or_delete_cache():
    """A crafted taskId with an arbitrary cacheKey must not read/delete it."""
    app = _make_background_app()
    manager = app.callback_map["output.children"]["manager"]
    client = app.server.test_client()

    manager.handle.set("operator-secret-key", {"secret": "topsecret"})

    forged = "slow_callback:1:operator-secret-key:0"
    for method in ("tasks/result", "tasks/get"):
        r = _post(client, method, {"taskId": forged})
        assert "topsecret" not in r.get_data(as_text=True)

    # The unrelated entry is neither disclosed nor deleted.
    assert manager.handle.get("operator-secret-key") == {"secret": "topsecret"}


def test_mcpbg019_legitimate_cancel_terminates_the_job():
    """The real signed taskId still cancels its own background job."""
    app = _make_background_app()
    client = app.server.test_client()

    r = _post(
        client,
        "tools/call",
        {"name": "slow_callback", "arguments": {"value": "hello"}},
    )
    task_info = json.loads(json.loads(r.data)["result"]["content"][0]["text"])
    task_id = task_info["taskId"]

    job_id, _ = _unwrap_handles(app, task_id)
    manager = app.callback_map["output.children"]["manager"]
    assert manager.job_running(job_id)

    r = _post(client, "tasks/cancel", {"taskId": task_id}, request_id=2)
    assert r.status_code == 200
    assert json.loads(r.data)["result"]["status"] == "cancelled"

    deadline = time.time() + 5
    while time.time() < deadline:
        if not manager.job_running(job_id):
            break
        time.sleep(0.1)
    assert not manager.job_running(job_id)
