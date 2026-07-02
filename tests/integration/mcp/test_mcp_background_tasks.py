"""Background callback support through the MCP HTTP endpoint.

End-to-end flows: trigger a background callback, poll via
``get_background_task_result``, observe progress (``set_progress``),
confirm the cache-expiry behavior, and verify the background-only tools
appear in ``tools/list``.
"""

import json
import re
import time

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
    job_id = task_id.split(":")[1]
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
    job_id = task_id.split(":")[1]

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
    cache_key = task_id.split(":")[2]

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
