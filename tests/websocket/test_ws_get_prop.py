"""WebSocket partial get_prop tests using specially constructed Store data."""

import asyncio
import json
import queue

import pytest

from dash import Dash, Input, Output, Patch, ctx, dcc, hooks, html, set_props
from dash._utils import stringify_id


@pytest.mark.parametrize("backend", ["fastapi", "quart"])
def test_wsgp001_partial_reads_from_store(dash_duo, backend):
    """Read all supported path shapes from one Store without changing it."""
    data = {
        "node1": {
            "node1-1": {"target": {"value": "event value"}},
            "records": [{"values": [0, False, "", None]}, {"values": [42]}],
        },
        "empty_list": [],
        "empty_dict": {},
        "a.b[0]": "literal key",
        "matrix": [[1, 2], [3, {"value": "nested list"}]],
    }
    app = Dash(__name__, backend=backend, websocket_callbacks=True)
    app.layout = html.Div(
        [
            dcc.Store(id="store", data=data),
            html.Button("Read", id="read"),
            html.Pre(id="result"),
            html.Div(id="observed"),
        ]
    )
    changes = []

    @app.callback(Output("observed", "children"), Input("store", "data"))
    def observe_data(value):
        changes.append(value)
        return str(len(changes))

    @app.callback(
        Output("result", "children"),
        Input("read", "n_clicks"),
        prevent_initial_call=True,
    )
    async def read_values(_):
        ws = ctx.websocket
        paths = {
            "nested_object": ["node1", "node1-1", "target", "value"],
            "list_subtree": ["node1", "records", 1],
            "negative_indices": ["node1", "records", -1, "values", -1],
            "zero": ["node1", "records", -2, "values", -4],
            "false": ["node1", "records", 0, "values", 1],
            "empty_string": ["node1", "records", 0, "values", 2],
            "null": ["node1", "records", 0, "values", 3],
            "missing": ["node1", "missing", "value"],
            "empty_list": ["empty_list"],
            "empty_dict": ["empty_dict"],
            "literal_key": ["a.b[0]"],
            "nested_list": ["matrix", -1, -1, "value"],
        }
        values = await asyncio.gather(
            *(ws.get_prop("store", "data", path=path) for path in paths.values())
        )
        result = dict(zip(paths, values))
        result["full"] = await ws.get_prop("store", "data", 5.0)
        result["none_path"] = await ws.get_prop("store", "data", path=None)
        result["empty_path"] = await ws.get_prop("store", "data", path=[])
        return json.dumps(result, ensure_ascii=False, sort_keys=True)

    expected = {
        "nested_object": "event value",
        "list_subtree": {"values": [42]},
        "negative_indices": 42,
        "zero": 0,
        "false": False,
        "empty_string": "",
        "null": None,
        "missing": None,
        "empty_list": [],
        "empty_dict": {},
        "literal_key": "literal key",
        "nested_list": "nested list",
        "full": data,
        "none_path": data,
        "empty_path": data,
    }

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#observed", "1")
    dash_duo.find_element("#read").click()
    dash_duo.wait_for_text_to_equal(
        "#result", json.dumps(expected, ensure_ascii=False, sort_keys=True)
    )
    assert changes == [data]
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("backend", ["fastapi", "quart"])
def test_wsgp002_current_state_patch_and_dict_id(dash_duo, backend):
    """Read browser edits, Patch updates, dict IDs, and a dynamic Store."""
    component_id = {"type": "store", "index": 0}
    app = Dash(__name__, backend=backend, websocket_callbacks=True)
    app.layout = html.Div(
        [
            dcc.Store(id=component_id, data={"records": [{"value": "initial"}]}),
            html.Button("Read", id="read"),
            html.Pre(id="result"),
            html.Div(id="container"),
        ]
    )

    @app.callback(
        Output("result", "children"),
        Input("read", "n_clicks"),
        prevent_initial_call=True,
    )
    async def read_callback(_):
        ws = ctx.websocket
        before = await ws.get_prop(
            stringify_id(component_id), "data", path=["records", -1, "value"]
        )
        patch = Patch()
        patch["records"].append({"value": "patched"})
        set_props(component_id, {"data": patch})
        after = await ws.get_prop(
            stringify_id(component_id), "data", path=["records", -1, "value"]
        )
        set_props(
            "container",
            {"children": dcc.Store(id="dynamic", data=[{"value": "dynamic"}])},
        )
        dynamic = await ws.get_prop("dynamic", "data", path=[-1, "value"])
        return json.dumps([before, after, dynamic])

    dash_duo.start_server(app)
    dash_duo.driver.execute_script(
        "window.dash_clientside.set_props(arguments[0], "
        "{data: {records: [{value: 'browser'}]}})",
        component_id,
    )
    dash_duo.find_element("#read").click()
    dash_duo.wait_for_text_to_equal("#result", '["browser", "patched", "dynamic"]')
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("dev_bundle", [False, True], ids=["production", "development"])
def test_wsgp003_wire_payload_excludes_unselected_data(
    dash_duo, ws_hook_cleanup, dev_bundle
):
    """Unselected Store data must not appear in a partial-read response."""
    responses = queue.Queue()

    @hooks.websocket_message()
    def capture_response(_websocket, message):
        if message.get("type") == "get_props_response":
            responses.put(message)
        return True

    def data(size):
        return {"selected": {"value": 42}, "large_sibling": "UNSELECTED" * size}

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)
    app.layout = html.Div(
        [
            dcc.Store(id="store", data=data(10000)),
            html.Button("Read", id="read"),
            html.Div(id="result"),
        ]
    )

    @app.callback(
        Output("result", "children"),
        Input("read", "n_clicks"),
        prevent_initial_call=True,
    )
    async def read_callback(_):
        for size in [10000, 50000]:
            set_props("store", {"data": data(size)})
            value = await ctx.websocket.get_prop(
                "store", "data", path=["selected", "value"]
            )
            if value != 42:
                return f"unexpected: {value}"
        return "done"

    dash_duo.start_server(app, dev_tools_serve_dev_bundles=dev_bundle)
    dash_duo.find_element("#read").click()
    dash_duo.wait_for_text_to_equal("#result", "done")
    messages = [responses.get(timeout=2) for _ in range(2)]
    assert responses.empty()
    assert len({message["requestId"] for message in messages}) == 2
    for message in messages:
        assert message["payload"] == {"data": 42}
        assert "UNSELECTED" not in json.dumps(message)
    assert len(json.dumps(messages[0]["payload"])) == len(
        json.dumps(messages[1]["payload"])
    )
    assert dash_duo.get_logs() == []
