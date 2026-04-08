"""Tests for background callback support via MCP Tasks API."""

import time

from dash import Dash, Input, Output, html
from dash._get_app import app_context
from dash.background_callback.managers.diskcache_manager import DiskcacheManager
from dash.mcp._server import _process_mcp_message
from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)


def _setup_mcp(app):
    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


def _msg(method, params=None, request_id=1):
    d = {"jsonrpc": "2.0", "method": method, "id": request_id}
    d["params"] = params if params is not None else {}
    return d


def _mcp(app, method, params=None, request_id=1):
    with app.server.test_request_context():
        _setup_mcp(app)
        return _process_mcp_message(_msg(method, params, request_id))


def _make_background_app():
    import diskcache

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


class TestCancelBackgroundTaskTool:
    """cancel_background_task tool wrapper."""

    def test_cancel_via_tool(self):
        import json

        app = _make_background_app()
        trigger = _mcp(
            app,
            "tools/call",
            {
                "name": "slow_callback",
                "arguments": {"value": "hello"},
            },
        )
        task_id = json.loads(trigger["result"]["content"][0]["text"])["taskId"]

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


class TestBackgroundToolRegistration:
    """Background task tools only appear when app has background callbacks."""

    def test_present_with_background_callbacks(self):
        app = _make_background_app()
        tools = _mcp(app, "tools/list")["result"]["tools"]
        names = [t["name"] for t in tools]
        assert "get_background_task_result" in names
        assert "cancel_background_task" in names

    def test_absent_without_background_callbacks(self):
        app = Dash(__name__)
        app.layout = html.Div([html.Div(id="in"), html.Div(id="out")])

        @app.callback(Output("out", "children"), Input("in", "children"))
        def normal_cb(v):
            return v

        tools = _mcp(app, "tools/list")["result"]["tools"]
        names = [t["name"] for t in tools]
        assert "get_background_task_result" not in names
        assert "cancel_background_task" not in names


class TestGetBackgroundTaskResult:
    """get_background_task_result tool: poll and retrieve results."""

    def _trigger(self, app):
        import json

        result = _mcp(
            app,
            "tools/call",
            {
                "name": "slow_callback",
                "arguments": {"value": "hello"},
            },
        )
        return json.loads(result["result"]["content"][0]["text"])["taskId"]

    def test_returns_working_while_running(self):
        app = _make_background_app()
        task_id = self._trigger(app)
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

    def test_returns_result_when_complete(self):
        app = _make_background_app()
        task_id = self._trigger(app)
        _, job_id, _ = task_id.split(":", 2)

        # Wait for completion
        manager = app.callback_map["output.children"]["manager"]
        deadline = time.time() + 3
        while time.time() < deadline:
            if not manager.job_running(job_id):
                break
            time.sleep(0.1)

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


class TestBackgroundCallbackTrigger:
    """Calling a background callback tool returns taskId immediately."""

    def test_returns_task_id(self):
        app = _make_background_app()
        result = _mcp(
            app,
            "tools/call",
            {
                "name": "slow_callback",
                "arguments": {"value": "hello"},
            },
        )
        text = result["result"]["content"][0]["text"]
        assert "taskId" in text
        assert "slow_callback:" in text


class TestTasksGet:
    """tasks/get derives status from the callback manager."""

    def test_working_status_while_running(self):
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

        # Immediately poll — job should still be running
        get_result = _mcp(app, "tasks/get", {"taskId": task_id})
        assert get_result["result"]["status"] == "working"
        assert get_result["result"]["taskId"] == task_id


class TestTasksResult:
    """tasks/result retrieves and formats the callback result."""

    def test_returns_formatted_result_when_complete(self):
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
        tool_name, job_id, cache_key = task_id.split(":", 2)

        # Wait for the background job to finish
        manager = app.callback_map["output.children"]["manager"]
        deadline = time.time() + 3
        while time.time() < deadline:
            if not manager.job_running(job_id):
                break
            time.sleep(0.1)

        # Fetch the result
        result = _mcp(app, "tasks/result", {"taskId": task_id})
        assert "content" in result["result"]
        text = result["result"]["content"][0]["text"]
        assert "done:" in text


class TestTasksCancel:
    """tasks/cancel terminates the background job."""

    def test_cancel_terminates_job(self):
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


class TestBackgroundCallbackWithTask:
    """When tools/call includes task metadata, return CreateTaskResult."""

    def test_returns_create_task_result(self):
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

    def test_task_id_encodes_tool_name_job_id_cache_key(self):
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
        tool_name, job_id, cache_key = task_id.split(":", 2)
        assert tool_name == "slow_callback"
        assert len(cache_key) == 64  # SHA256 hex
