"""Background callback support through the MCP HTTP endpoint.

End-to-end flows: trigger a background callback, poll via
``get_background_task_result``, observe progress (``set_progress``),
confirm the cache-expiry behavior, and verify the background-only tools
appear in ``tools/list``.
"""

import json
import re
import time
from datetime import datetime

import diskcache
from dash import Dash, Input, Output, html
from dash.background_callback.managers.diskcache_manager import DiskcacheManager

MCP_PATH = "_mcp"


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

    # Read createdAt from the callback manager directly
    _, _, cache_key = task_id.split(":", 2)
    stored_created_at = app.callback_map["output.children"]["manager"].handle.get(
        f"{cache_key}-created_at"
    )
    assert stored_created_at is not None

    # Poll — should be working, with createdAt matching the stored value
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
    assert datetime.fromisoformat(poll_data["createdAt"]) == datetime.fromisoformat(
        stored_created_at
    )

    # Wait for completion
    _, job_id, _ = task_id.split(":", 2)
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
    """Result and createdAt are available until the cache expires."""
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

    # Trigger
    r = _post(
        client,
        "tools/call",
        {"name": "fast_cb", "arguments": {"value": "hi"}},
    )
    task_info = json.loads(json.loads(r.data)["result"]["content"][0]["text"])
    task_id = task_info["taskId"]
    _, job_id, cache_key = task_id.split(":", 2)

    # Wait for job to finish
    deadline = time.time() + 3
    while time.time() < deadline:
        if not manager.job_running(job_id):
            break
        time.sleep(0.1)

    # First retrieval — result and createdAt available
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
    assert "done:" in text
    created_at = manager.handle.get(f"{cache_key}-created_at")
    assert created_at is not None

    # Second retrieval — still available (cache_by keeps it)
    r = _post(
        client,
        "tools/call",
        {
            "name": "get_background_task_result",
            "arguments": {"taskId": task_id},
        },
        request_id=3,
    )
    text = json.loads(r.data)["result"]["content"][0]["text"]
    assert "done:" in text
    assert manager.handle.get(f"{cache_key}-created_at") == created_at

    # Wait for expiry
    time.sleep(2.5)

    # After expiry — tool reports failure, createdAt is fresh (stored value gone)
    r = _post(
        client,
        "tools/call",
        {
            "name": "get_background_task_result",
            "arguments": {"taskId": task_id},
        },
        request_id=4,
    )
    poll_data = json.loads(json.loads(r.data)["result"]["content"][0]["text"])
    assert poll_data["status"] == "failed"
    assert datetime.fromisoformat(poll_data["createdAt"]) > datetime.fromisoformat(
        created_at
    )


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
