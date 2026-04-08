"""Background callback support via MCP Tasks.

Covers both layers:
- Layer 1 (``dash/mcp/tasks/``): ``tasks/get``, ``tasks/result``, ``tasks/cancel``
  derived on-demand from the callback manager.
- Layer 2 (tool wrappers): ``get_background_task_result`` and
  ``cancel_background_task`` — only registered when the app has
  background callbacks.
"""

import json
import time

import diskcache
from dash import Dash, Input, Output, html
from dash.background_callback.managers.diskcache_manager import DiskcacheManager
from dash.mcp._server import _process_mcp_message

from tests.unit.mcp.conftest import _setup_mcp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _msg(method, params=None, request_id=1):
    d = {"jsonrpc": "2.0", "method": method, "id": request_id}
    d["params"] = params if params is not None else {}
    return d


def _mcp(app, method, params=None, request_id=1):
    with app.server.test_request_context():
        _setup_mcp(app)
        return _process_mcp_message(_msg(method, params, request_id))


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
        """A background callback."""
        time.sleep(0.3)
        return f"done: {value}"

    return app


def _trigger_task(app):
    """Call slow_callback via tools/call and return its taskId."""
    result = _mcp(
        app,
        "tools/call",
        {"name": "slow_callback", "arguments": {"value": "hello"}},
    )
    return json.loads(result["result"]["content"][0]["text"])["taskId"]


def _wait_for_completion(app, task_id, timeout=3):
    """Block until the callback manager reports the job is no longer running."""
    _, job_id, _ = task_id.split(":", 2)
    manager = app.callback_map["output.children"]["manager"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not manager.job_running(job_id):
            return
        time.sleep(0.1)


# ---------------------------------------------------------------------------
# Tool-layer: cancel_background_task, get_background_task_result, registration
# ---------------------------------------------------------------------------


def test_mcpbg001_cancel_via_tool():
    app = _make_background_app()
    task_id = _trigger_task(app)

    cancel = _mcp(
        app,
        "tools/call",
        {
            "name": "cancel_background_task",
            "arguments": {"taskId": task_id},
        },
    )
    assert cancel["result"].get("isError") is not True

    _, job_id, _ = task_id.split(":", 2)
    manager = app.callback_map["output.children"]["manager"]
    assert not manager.job_running(job_id)


def test_mcpbg002_present_with_background_callbacks():
    app = _make_background_app()
    tools = _mcp(app, "tools/list")["result"]["tools"]
    names = [t["name"] for t in tools]
    assert "get_background_task_result" in names
    assert "cancel_background_task" in names


def test_mcpbg003_absent_without_background_callbacks():
    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="in"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("in", "children"))
    def normal_cb(v):
        return v

    tools = _mcp(app, "tools/list")["result"]["tools"]
    names = [t["name"] for t in tools]
    assert "get_background_task_result" not in names
    assert "cancel_background_task" not in names


def test_mcpbg004_returns_working_while_running():
    app = _make_background_app()
    task_id = _trigger_task(app)
    poll = _mcp(
        app,
        "tools/call",
        {
            "name": "get_background_task_result",
            "arguments": {"taskId": task_id},
        },
    )
    text = poll["result"]["content"][0]["text"]
    assert "working" in text.lower()


def test_mcpbg005_returns_result_when_complete():
    app = _make_background_app()
    task_id = _trigger_task(app)
    _wait_for_completion(app, task_id)

    result = _mcp(
        app,
        "tools/call",
        {
            "name": "get_background_task_result",
            "arguments": {"taskId": task_id},
        },
    )
    text = result["result"]["content"][0]["text"]
    assert "done:" in text


def test_mcpbg006_returns_task_id():
    """Calling a background callback tool returns a taskId immediately."""
    app = _make_background_app()
    result = _mcp(
        app,
        "tools/call",
        {"name": "slow_callback", "arguments": {"value": "hello"}},
    )
    text = result["result"]["content"][0]["text"]
    assert "taskId" in text
    assert "slow_callback:" in text


# ---------------------------------------------------------------------------
# Tasks-protocol layer: tasks/get, tasks/result, tasks/cancel
# ---------------------------------------------------------------------------


def test_mcpbg007_tasks_get_working_status_while_running():
    app = _make_background_app()
    create_result = _mcp(
        app,
        "tools/call",
        {
            "name": "slow_callback",
            "arguments": {"value": "hello"},
            "task": {"ttl": 60000},
        },
    )
    task_id = create_result["result"]["task"]["taskId"]

    get_result = _mcp(app, "tasks/get", {"taskId": task_id})
    assert get_result["result"]["status"] == "working"
    assert get_result["result"]["taskId"] == task_id


def test_mcpbg008_tasks_result_returns_formatted_result():
    app = _make_background_app()
    create_result = _mcp(
        app,
        "tools/call",
        {
            "name": "slow_callback",
            "arguments": {"value": "hello"},
            "task": {"ttl": 60000},
        },
    )
    task_id = create_result["result"]["task"]["taskId"]
    _wait_for_completion(app, task_id)

    result = _mcp(app, "tasks/result", {"taskId": task_id})
    assert "content" in result["result"]
    text = result["result"]["content"][0]["text"]
    assert "done:" in text


def test_mcpbg009_tasks_cancel_terminates_job():
    app = _make_background_app()
    create_result = _mcp(
        app,
        "tools/call",
        {
            "name": "slow_callback",
            "arguments": {"value": "hello"},
            "task": {"ttl": 60000},
        },
    )
    task_id = create_result["result"]["task"]["taskId"]

    cancel_result = _mcp(app, "tasks/cancel", {"taskId": task_id})
    assert "error" not in cancel_result

    _, job_id, _ = task_id.split(":", 2)
    manager = app.callback_map["output.children"]["manager"]
    assert not manager.job_running(job_id)


# ---------------------------------------------------------------------------
# tools/call with task metadata → CreateTaskResult + taskId encoding
# ---------------------------------------------------------------------------


def test_mcpbg010_returns_create_task_result():
    app = _make_background_app()
    result = _mcp(
        app,
        "tools/call",
        {
            "name": "slow_callback",
            "arguments": {"value": "hello"},
            "task": {"ttl": 60000},
        },
    )
    task = result["result"]["task"]
    assert task["status"] == "working"
    assert "taskId" in task
    assert "pollInterval" in task


def test_mcpbg011_task_id_encodes_tool_name_job_id_cache_key():
    app = _make_background_app()
    result = _mcp(
        app,
        "tools/call",
        {
            "name": "slow_callback",
            "arguments": {"value": "hello"},
            "task": {"ttl": 60000},
        },
    )
    task_id = result["result"]["task"]["taskId"]
    tool_name, _job_id, cache_key = task_id.split(":", 2)
    assert tool_name == "slow_callback"
    assert len(cache_key) == 64  # SHA256 hex
