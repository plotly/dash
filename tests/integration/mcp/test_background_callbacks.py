"""Integration tests for background callback support via MCP."""

import json
import time

import diskcache
from dash import Dash, Input, Output, html
from dash.background_callback.managers.diskcache_manager import DiskcacheManager

MCP_PATH = "_mcp"


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


def _post(client, method, params=None, session_id=None, request_id=1):
    headers = {"Content-Type": "application/json"}
    if session_id:
        headers["mcp-session-id"] = session_id
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
        headers=headers,
    )


def _init_session(client):
    r = _post(client, "initialize")
    return r.headers["mcp-session-id"]


class TestBackgroundCallbackLifecycle:
    """Full lifecycle: trigger → poll → get result, over HTTP."""

    def test_trigger_poll_and_retrieve(self):
        app = _make_background_app()
        client = app.server.test_client()
        sid = _init_session(client)

        # Trigger
        r = _post(
            client,
            "tools/call",
            {
                "name": "slow_callback",
                "arguments": {"value": "hello"},
            },
            session_id=sid,
        )
        assert r.status_code == 200
        data = json.loads(r.data)
        task_info = json.loads(data["result"]["content"][0]["text"])
        task_id = task_info["taskId"]
        assert task_info["status"] == "working"

        # Poll — should be working initially
        r = _post(
            client,
            "tools/call",
            {
                "name": "get_background_task_result",
                "arguments": {"taskId": task_id},
            },
            session_id=sid,
            request_id=2,
        )
        assert r.status_code == 200

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
            session_id=sid,
            request_id=3,
        )
        assert r.status_code == 200
        data = json.loads(r.data)
        text = data["result"]["content"][0]["text"]
        assert "done:" in text

    def test_background_tools_in_tools_list(self):
        app = _make_background_app()
        client = app.server.test_client()
        sid = _init_session(client)

        r = _post(client, "tools/list", session_id=sid)
        data = json.loads(r.data)
        names = [t["name"] for t in data["result"]["tools"]]
        assert "get_background_task_result" in names
        assert "cancel_background_task" in names
        assert "slow_callback" in names
