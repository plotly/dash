import pytest

from dash import Dash, Input, Output, html, dcc
from dash.dash_table import DataTable


test_cases = {
    "not-boolean": {
        "fail": True,
        "name": 'simple "not a boolean" check',
        "component": dcc.Input,
        "props": {"multiple": 0},
    },
    "missing-required-nested-prop": {
        "fail": True,
        "name": 'missing required "value" inside options',
        "component": dcc.Checklist,
        "props": {"options": [{"label": "hello"}], "value": ["test"]},
    },
    "invalid-arrayOf": {
        "fail": True,
        "name": "invalid arrayOf",
        "component": dcc.Checklist,
        "props": {"options": "test", "value": []},
    },
    "invalid-oneOf": {
        "fail": True,
        "name": "invalid oneOf",
        "component": dcc.Input,
        "props": {"type": "test"},
    },
    "invalid-oneOfType": {
        "fail": True,
        "name": "invalid oneOfType",
        "component": dcc.Input,
        "props": {"max": True},
    },
    "invalid-shape-1": {
        "fail": True,
        "name": "invalid key within nested object",
        "component": DataTable,
        "props": {"active_cell": {"asdf": "that"}},
    },
    "invalid-shape-2": {
        "fail": True,
        "name": "nested object with bad value",
        "component": DataTable,
        "props": {
            "columns": [{"id": "id", "name": "name", "format": {"locale": "asdf"}}]
        },
    },
    "invalid-shape-3": {
        "fail": True,
        "name": "invalid oneOf within nested object",
        "component": DataTable,
        "props": {
            "columns": [{"id": "id", "name": "name", "on_change": {"action": "asdf"}}]
        },
    },
    "invalid-shape-4": {
        "fail": True,
        "name": "invalid key within deeply nested object",
        "component": DataTable,
        "props": {
            "columns": [{"id": "id", "name": "name", "on_change": {"asdf": "asdf"}}]
        },
    },
    "invalid-shape-5": {
        "fail": True,
        "name": "invalid not required key",
        "component": dcc.Dropdown,
        "props": {"options": [{"label": "new york", "value": "ny", "typo": "asdf"}]},
    },
    "string-not-list": {
        "fail": True,
        "name": "string-not-a-list",
        "component": dcc.Checklist,
        "props": {"options": [{"label": "hello", "value": "test"}], "value": "test"},
    },
    "no-properties": {
        "fail": False,
        "name": "no properties",
        "component": dcc.Input,
        "props": {},
    },
    "nested-children": {
        "fail": True,
        "name": "nested children",
        "component": html.Div,
        "props": {"children": [[1]]},
    },
    "deeply-nested-children": {
        "fail": True,
        "name": "deeply nested children",
        "component": html.Div,
        "props": {"children": html.Div([html.Div([3, html.Div([[10]])])])},
    },
    "dict": {
        "fail": True,
        "name": "returning a dictionary",
        "component": html.Div,
        "props": {"children": {"hello": "world"}},
    },
    "nested-prop-failure": {
        "fail": True,
        "name": "nested string instead of number/null",
        "component": DataTable,
        "props": {
            "columns": [{"id": "id", "name": "name", "format": {"prefix": "asdf"}}]
        },
    },
    "allow-nested-prop": {
        "fail": False,
        "name": "allow nested prop",
        "component": dcc.Checklist,
        "props": {"options": [{"label": "hello", "value": True}], "value": ["test"]},
    },
    "allow-null": {
        "fail": False,
        "name": "nested null",
        "component": DataTable,
        "props": {
            "columns": [{"id": "id", "name": "name", "format": {"prefix": None}}]
        },
    },
    "allow-null-2": {
        "fail": False,
        "name": "allow null as value",
        "component": dcc.Dropdown,
        "props": {"value": None},
    },
    "allow-null-3": {
        "fail": False,
        "logs": True,
        "name": "allow null in properties",
        "component": dcc.Input,
        "props": {"value": None},
    },
    "allow-null-4": {
        "fail": False,
        "name": "allow null in oneOfType",
        "component": dcc.Store,
        "props": {"id": "store", "data": None},
    },
    "long-property-string": {
        "fail": True,
        "name": "long property string with id",
        "component": html.Div,
        "props": {"id": "pink div", "style": "color: hotpink; " * 1000},
    },
    "multiple-wrong-values": {
        "fail": True,
        "name": "multiple wrong props",
        "component": dcc.Dropdown,
        "props": {"id": "dropdown", "value": 10, "options": "asdf"},
    },
    "boolean-html-properties": {
        "fail": True,
        "name": "dont allow booleans for dom props",
        "component": html.Div,
        "props": {"contentEditable": True},
    },
    "allow-exact-with-optional-and-required-1": {
        "fail": False,
        "name": "allow exact with optional and required keys",
        "component": dcc.Dropdown,
        "props": {"options": [{"label": "new york", "value": "ny", "disabled": False}]},
    },
    "allow-exact-with-optional-and-required-2": {
        "fail": False,
        "name": "allow exact with optional and required keys 2",
        "component": dcc.Dropdown,
        "props": {"options": [{"label": "new york", "value": "ny"}]},
    },
}


@pytest.mark.skip(
    reason="Flaky error on CI: https://github.com/plotly/dash/issues/2654"
)
def test_dvpc001_prop_check_errors_with_path(dash_duo):
    app = Dash(__name__, eager_loading=True)

    app.layout = html.Div([html.Div(id="content"), dcc.Location(id="location")])

    @app.callback(Output("content", "children"), [Input("location", "pathname")])
    def display_content(pathname):
        if pathname is None or pathname == "/":
            return "Initial state"
        test_case = test_cases[pathname.strip("/")]
        return html.Div(
            id="new-component", children=test_case["component"](**test_case["props"])
        )

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    for tc in test_cases:
        route_url = "{}/{}".format(dash_duo.server_url, tc)
        dash_duo.wait_for_page(url=route_url)

        fail = test_cases[tc]["fail"]
        logs = test_cases[tc].get("logs", fail)

        if fail:
            dash_duo.wait_for_element(".test-devtools-error-toggle").click()
            dash_duo.wait_for_element(".dash-fe-error__info")
            dash_duo.percy_snapshot(
                "devtools validation exception: {}".format(test_cases[tc]["name"])
            )
        else:
            dash_duo.wait_for_element("#new-component")
            dash_duo.wait_for_no_elements(".test-devtools-error-toggle")

        if logs:
            assert dash_duo.get_logs(), tc
        else:
            assert dash_duo.get_logs() == [], tc
