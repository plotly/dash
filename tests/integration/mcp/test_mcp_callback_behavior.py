"""Callback behaviors surfaced through MCP tools (end-to-end).

Covers the full pipeline — a real Dash server via ``dash_duo`` + the MCP
HTTP endpoint — for every callback signature variant and the surrounding
tool-list conventions:

- Positional, dict-based, and tuple-grouped ``inputs`` / ``state`` /
  ``output`` forms.
- ``State``, multi-output, ``PreventUpdate``-style no-output callbacks,
  ``ctx.triggered_id``, pattern-matching (``ALL``/``MATCH``/``ALLSMALLER``).
- Initial values: ``prevent_initial_call`` vs. initial-callback overrides.
- Duplicate outputs (``allow_duplicate=True``) appearing as separate tools.
- ``tools/list`` naming rules (64-char limit, uniqueness, built-ins).
- A representative input-schema smoke test (label + DatePicker).
- ``get_dash_component`` structured output via HTTP.
"""

from dash import (
    ALL,
    ALLSMALLER,
    MATCH,
    Dash,
    Input,
    Output,
    State,
    ctx,
    dcc,
    html,
    set_props,
)

from tests.integration.mcp.conftest import _mcp_call_tool, _mcp_tools


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_tool(tools, name):
    return next((t for t in tools if t["name"] == name), None)


def _get_response(result):
    return result["result"]["structuredContent"]["response"]


# ---------------------------------------------------------------------------
# Callback signatures — positional, multi-output, State, dict-based, tuples
# ---------------------------------------------------------------------------


def test_mcpb001_positional_callback(dash_duo):
    """Standard positional: Input("fruit", "value") → param named 'value'."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="fruit", options=["apple", "banana"], value="apple"),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("fruit", "value"))
    def show_fruit(value):
        return f"Selected: {value}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "Selected: apple")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "show_fruit")
    props = tool["inputSchema"]["properties"]

    assert set(props.keys()) == {"value"}
    assert any(s.get("type") == "string" for s in props["value"]["anyOf"])

    value_desc = props["value"].get("description", "")
    assert "value: 'apple'" in value_desc
    assert "options: ['apple', 'banana']" in value_desc

    result = _mcp_call_tool(dash_duo.server.url, "show_fruit", {"value": "apple"})
    response = _get_response(result)
    assert response["out"]["children"] == "Selected: apple"

    result = _mcp_call_tool(dash_duo.server.url, "show_fruit", {"value": "banana"})
    response = _get_response(result)
    assert response["out"]["children"] == "Selected: banana"


def test_mcpb002_positional_with_state(dash_duo):
    """Positional with State: Input + State both appear as params."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            dcc.Input(id="inp", value="hello"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        State("inp", "value"),
    )
    def update(n_clicks, value):
        return f"Clicked {n_clicks} with {value}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "Clicked None with hello")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "update")
    props = tool["inputSchema"]["properties"]

    assert set(props.keys()) == {"n_clicks", "value"}
    assert any(s.get("type") == "number" for s in props["n_clicks"]["anyOf"])

    assert "value: 'hello'" in props["value"].get("description", "")

    result = _mcp_call_tool(
        dash_duo.server.url, "update", {"n_clicks": None, "value": "hello"}
    )
    response = _get_response(result)
    assert response["out"]["children"] == "Clicked None with hello"

    result = _mcp_call_tool(
        dash_duo.server.url, "update", {"n_clicks": 3, "value": "world"}
    )
    response = _get_response(result)
    assert response["out"]["children"] == "Clicked 3 with world"


def test_mcpb003_multi_output_positional(dash_duo):
    """Multi-output: returns tuple → both outputs updated in response."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="inp", value="test"),
            html.Div(id="out1"),
            html.Div(id="out2"),
        ]
    )

    @app.callback(
        Output("out1", "children"),
        Output("out2", "children"),
        Input("inp", "value"),
    )
    def split_case(value):
        return value.upper(), value.lower()

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out1", "TEST")
    dash_duo.wait_for_text_to_equal("#out2", "test")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "split_case")
    props = tool["inputSchema"]["properties"]
    assert set(props.keys()) == {"value"}

    assert "value: 'test'" in props["value"].get("description", "")

    result = _mcp_call_tool(dash_duo.server.url, "split_case", {"value": "test"})
    response = _get_response(result)
    assert response["out1"]["children"] == "TEST"
    assert response["out2"]["children"] == "test"


def test_mcpb004_dict_based_inputs_and_state(dash_duo):
    """Dict-based: inputs=dict(trigger=...), state=dict(name=...) → dict keys are params."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            dcc.Input(id="name-input", value="world"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        inputs=dict(trigger=Input("btn", "n_clicks")),
        state=dict(name=State("name-input", "value")),
    )
    def greet(trigger, name):
        return f"Hello, {name}!"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "Hello, world!")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "greet")
    props = tool["inputSchema"]["properties"]

    assert set(props.keys()) == {"trigger", "name"}
    assert any(s.get("type") == "number" for s in props["trigger"]["anyOf"])

    result = _mcp_call_tool(
        dash_duo.server.url, "greet", {"trigger": None, "name": "world"}
    )
    response = _get_response(result)
    assert response["out"]["children"] == "Hello, world!"

    result = _mcp_call_tool(
        dash_duo.server.url, "greet", {"trigger": 1, "name": "Dash"}
    )
    response = _get_response(result)
    assert response["out"]["children"] == "Hello, Dash!"


def test_mcpb005_dict_based_outputs(dash_duo):
    """Dict-based outputs: output=dict(...) → callback returns dict, both outputs updated."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="inp", value="hello"),
            html.Div(id="upper-out"),
            html.Div(id="lower-out"),
        ]
    )

    @app.callback(
        output=dict(
            upper=Output("upper-out", "children"),
            lower=Output("lower-out", "children"),
        ),
        inputs=dict(val=Input("inp", "value")),
    )
    def transform(val):
        return dict(upper=val.upper(), lower=val.lower())

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#upper-out", "HELLO")
    dash_duo.wait_for_text_to_equal("#lower-out", "hello")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "transform")
    props = tool["inputSchema"]["properties"]
    assert set(props.keys()) == {"val"}

    result = _mcp_call_tool(dash_duo.server.url, "transform", {"val": "hello"})
    response = _get_response(result)
    assert response["upper-out"]["children"] == "HELLO"
    assert response["lower-out"]["children"] == "hello"


def test_mcpb006_mixed_input_state_in_inputs(dash_duo):
    """Mixed: State inside inputs=dict alongside Input → all appear as params."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            dcc.Input(id="first", value="Jane"),
            dcc.Input(id="last", value="Doe"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        inputs=dict(
            clicks=Input("btn", "n_clicks"),
            first=State("first", "value"),
            last=State("last", "value"),
        ),
    )
    def full_name(clicks, first, last):
        return f"{first} {last}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "Jane Doe")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "full_name")
    props = tool["inputSchema"]["properties"]

    assert set(props.keys()) == {"clicks", "first", "last"}
    assert any(s.get("type") == "number" for s in props["clicks"]["anyOf"])

    result = _mcp_call_tool(
        dash_duo.server.url,
        "full_name",
        {"clicks": None, "first": "Jane", "last": "Doe"},
    )
    response = _get_response(result)
    assert response["out"]["children"] == "Jane Doe"

    result = _mcp_call_tool(
        dash_duo.server.url,
        "full_name",
        {"clicks": 1, "first": "John", "last": "Smith"},
    )
    response = _get_response(result)
    assert response["out"]["children"] == "John Smith"


def test_mcpb007_tuple_grouped_inputs(dash_duo):
    """Tuple grouping: pair=(Input("a",...), Input("b",...)) → expands to two named params."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="a", value="1"),
            dcc.Input(id="b", value="2"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        inputs=dict(pair=(Input("a", "value"), Input("b", "value"))),
    )
    def combine(pair):
        return f"{pair[0]}+{pair[1]}"

    dash_duo.start_server(app)
    tool = _find_tool(_mcp_tools(dash_duo.server.url), "combine")
    props = tool["inputSchema"]["properties"]

    assert set(props.keys()) == {"pair_a__value", "pair_b__value"}
    for schema in props.values():
        assert any(s.get("type") == "string" for s in schema["anyOf"])

    result = _mcp_call_tool(
        dash_duo.server.url,
        "combine",
        {"pair_a__value": "x", "pair_b__value": "y"},
    )
    response = _get_response(result)
    assert response["out"]["children"] == "x+y"


def test_mcpb008_initial_values_from_chained_callbacks(dash_duo):
    """Querying components reflects post-initial-callback values.

    3-link chain: country (default "France") → update_states →
    state (should become "Ile-de-France") → update_cities →
    city (should become "Paris").
    """
    DATA = {
        "France": {
            "Ile-de-France": ["Paris", "Versailles"],
            "Provence": ["Marseille", "Nice"],
        },
        "Germany": {
            "Bavaria": ["Munich", "Nuremberg"],
            "Berlin": ["Berlin"],
        },
    }

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="country", options=list(DATA.keys()), value="France"),
            dcc.Dropdown(id="state"),
            dcc.Dropdown(id="city"),
        ]
    )

    @app.callback(
        Output("state", "options"),
        Output("state", "value"),
        Input("country", "value"),
    )
    def update_states(country):
        if not country:
            return [], None
        states = list(DATA[country].keys())
        return [{"label": s, "value": s} for s in states], states[0]

    @app.callback(
        Output("city", "options"),
        Output("city", "value"),
        Input("state", "value"),
        Input("country", "value"),
    )
    def update_cities(state, country):
        if not state or not country:
            return [], None
        cities = DATA[country][state]
        return [{"label": c, "value": c} for c in cities], cities[0]

    dash_duo.start_server(app)

    tools = _mcp_tools(dash_duo.server.url)
    update_cities_tool = _find_tool(tools, "update_cities")
    state_desc = update_cities_tool["inputSchema"]["properties"]["state"].get(
        "description", ""
    )
    assert "Ile-de-France" in state_desc

    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "state", "property": "value"},
    )
    state_props = result["result"]["structuredContent"]["properties"]
    assert state_props["value"]["initial_value"] == "Ile-de-France"

    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "city", "property": "value"},
    )
    city_props = result["result"]["structuredContent"]["properties"]
    assert city_props["value"]["initial_value"] == "Paris"


def test_mcpb009_dict_based_reordered_state_input(dash_duo):
    """Dict-based callback with State before Input: call works, schema types correct.

    State is listed before Input in the dict. The callback should still
    work correctly via MCP, and the schema types should match the
    function annotations (name: str, trigger: int), not be swapped.
    """
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            dcc.Input(id="inp", value="World"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        inputs=dict(name=State("inp", "value"), trigger=Input("btn", "n_clicks")),
    )
    def greet(name: str, trigger: int):
        return f"Hello {name}"

    dash_duo.start_server(app)

    result = _mcp_call_tool(
        dash_duo.server.url,
        "greet",
        {"name": "Dash", "trigger": 1},
    )
    assert _get_response(result)["out"]["children"] == "Hello Dash"

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "greet")
    props = tool["inputSchema"]["properties"]
    assert props["trigger"]["type"] == "integer"
    assert props["name"]["type"] == "string"

    trigger_desc = props["trigger"].get("description", "")
    assert "number of times that this element has been clicked on" in trigger_desc
    name_desc = props["name"].get("description", "")
    assert "The value of the input" in name_desc


# ---------------------------------------------------------------------------
# Pattern-matching callbacks (ALL / MATCH / ALLSMALLER)
# ---------------------------------------------------------------------------


def test_mcpb010_pattern_matching_callback(dash_duo):
    """Pattern-matching dict IDs: tool works with correct params and results."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id={"type": "field", "index": 0}, value="hello"),
            dcc.Input(id={"type": "field", "index": 1}, value="world"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input({"type": "field", "index": 0}, "value"),
        Input({"type": "field", "index": 1}, "value"),
    )
    def combine(first, second):
        return f"{first} {second}"

    dash_duo.start_server(app)

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "combine")
    assert tool is not None
    props = tool["inputSchema"]["properties"]
    assert "first" in props
    assert "second" in props

    dash_duo.wait_for_text_to_equal("#out", "hello world")
    result = _mcp_call_tool(
        dash_duo.server.url,
        "combine",
        {"first": "hello", "second": "world"},
    )
    response = _get_response(result)
    assert response["out"]["children"] == "hello world"

    result = _mcp_call_tool(
        dash_duo.server.url,
        "combine",
        {"first": "foo", "second": "bar"},
    )
    response = _get_response(result)
    assert response["out"]["children"] == "foo bar"


def test_mcpb011_pattern_matching_with_all_wildcard(dash_duo):
    """ALL wildcard: one callback receives values from all matching components."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id={"type": "input", "index": 0}, value="alpha"),
            dcc.Input(id={"type": "input", "index": 1}, value="beta"),
            html.Div(id="summary"),
        ]
    )

    @app.callback(
        Output("summary", "children"),
        Input({"type": "input", "index": ALL}, "value"),
    )
    def summarize(values):
        return ", ".join(v for v in values if v)

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#summary", "alpha, beta")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "summarize")
    assert tool is not None

    values_schema = tool["inputSchema"]["properties"]["values"]
    assert (
        values_schema["type"] == "array"
    ), f"ALL wildcard param should be typed as array, got: {values_schema}"
    assert "items" in values_schema, "Array schema should include items definition"
    items = values_schema["items"]
    assert items["type"] == "object"
    assert "id" in items["properties"]
    assert "value" in items["properties"]
    assert "Pattern-matching input (ALL)" in values_schema.get(
        "description", ""
    ), "ALL wildcard param description should explain the pattern-matching behavior"

    result = _mcp_call_tool(
        dash_duo.server.url,
        "summarize",
        {
            "values": [
                {
                    "id": {"type": "input", "index": 0},
                    "property": "value",
                    "value": "alpha",
                },
                {
                    "id": {"type": "input", "index": 1},
                    "property": "value",
                    "value": "beta",
                },
            ]
        },
    )
    response = _get_response(result)
    assert response["summary"]["children"] == "alpha, beta"

    result = _mcp_call_tool(
        dash_duo.server.url,
        "summarize",
        {
            "values": [
                {
                    "id": {"type": "input", "index": 0},
                    "property": "value",
                    "value": "one",
                },
                {
                    "id": {"type": "input", "index": 1},
                    "property": "value",
                    "value": "two",
                },
            ]
        },
    )
    response = _get_response(result)
    assert response["summary"]["children"] == "one, two"


def test_mcpb012_pattern_matching_mixed_outputs(dash_duo):
    """Mixed outputs: one regular + one ALL wildcard in the same callback."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id={"type": "field", "index": 0}, value="a"),
            dcc.Input(id={"type": "field", "index": 1}, value="b"),
            html.Div(id={"type": "echo", "index": 0}),
            html.Div(id={"type": "echo", "index": 1}),
            html.Div(id="total"),
        ]
    )

    @app.callback(
        Output({"type": "echo", "index": ALL}, "children"),
        Output("total", "children"),
        Input({"type": "field", "index": ALL}, "value"),
    )
    def echo_and_total(values):
        echoes = [f"Echo: {v}" for v in values]
        total = f"Total: {len(values)} items"
        return echoes, total

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#total", "Total: 2 items")

    result = _mcp_call_tool(
        dash_duo.server.url,
        "echo_and_total",
        {
            "values": [
                {
                    "id": {"type": "field", "index": 0},
                    "property": "value",
                    "value": "x",
                },
                {
                    "id": {"type": "field", "index": 1},
                    "property": "value",
                    "value": "y",
                },
            ]
        },
    )
    response = _get_response(result)
    assert response["total"]["children"] == "Total: 2 items"


def test_mcpb013_pattern_matching_with_match_wildcard(dash_duo):
    """MATCH wildcard: callback fires per-component with matching index.

    Based on https://dash.plotly.com/pattern-matching-callbacks
    """
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                ["NYC", "MTL", "LA", "TOKYO"],
                "NYC",
                id={"type": "city-dd", "index": 0},
            ),
            html.Div(id={"type": "city-out", "index": 0}),
            dcc.Dropdown(
                ["NYC", "MTL", "LA", "TOKYO"],
                "LA",
                id={"type": "city-dd", "index": 1},
            ),
            html.Div(id={"type": "city-out", "index": 1}),
        ]
    )

    @app.callback(
        Output({"type": "city-out", "index": MATCH}, "children"),
        Input({"type": "city-dd", "index": MATCH}, "value"),
    )
    def show_city(value):
        return f"Selected: {value}"

    dash_duo.start_server(app)

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "show_city")
    assert tool is not None

    value_schema = tool["inputSchema"]["properties"]["value"]
    assert "Pattern-matching input (MATCH)" in value_schema.get("description", "")

    result = _mcp_call_tool(
        dash_duo.server.url,
        "show_city",
        {
            "value": {
                "id": {"type": "city-dd", "index": 0},
                "property": "value",
                "value": "MTL",
            }
        },
    )
    response = _get_response(result)
    out_key = next(k for k in response if "city-out" in k)
    assert response[out_key]["children"] == "Selected: MTL"


def test_mcpb014_pattern_matching_with_allsmaller_wildcard(dash_duo):
    """ALLSMALLER wildcard: receives values from components with smaller index.

    Based on https://dash.plotly.com/pattern-matching-callbacks
    """
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                ["France", "Germany", "Japan"],
                "France",
                id={"type": "country-dd", "index": 0},
            ),
            html.Div(id={"type": "country-out", "index": 0}),
            dcc.Dropdown(
                ["France", "Germany", "Japan"],
                "Germany",
                id={"type": "country-dd", "index": 1},
            ),
            html.Div(id={"type": "country-out", "index": 1}),
            dcc.Dropdown(
                ["France", "Germany", "Japan"],
                "Japan",
                id={"type": "country-dd", "index": 2},
            ),
            html.Div(id={"type": "country-out", "index": 2}),
        ]
    )

    @app.callback(
        Output({"type": "country-out", "index": MATCH}, "children"),
        Input({"type": "country-dd", "index": MATCH}, "value"),
        Input({"type": "country-dd", "index": ALLSMALLER}, "value"),
    )
    def show_countries(current, previous):
        all_selected = [current] + list(reversed(previous))
        return f"All: {', '.join(all_selected)}"

    dash_duo.start_server(app)

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "show_countries")
    assert tool is not None

    props = tool["inputSchema"]["properties"]
    assert "Pattern-matching input (MATCH)" in props["current"].get("description", "")
    assert "Pattern-matching input (ALLSMALLER)" in props["previous"].get(
        "description", ""
    )

    result = _mcp_call_tool(
        dash_duo.server.url,
        "show_countries",
        {
            "current": {
                "id": {"type": "country-dd", "index": 2},
                "property": "value",
                "value": "Japan",
            },
            "previous": [
                {
                    "id": {"type": "country-dd", "index": 0},
                    "property": "value",
                    "value": "France",
                },
                {
                    "id": {"type": "country-dd", "index": 1},
                    "property": "value",
                    "value": "Germany",
                },
            ],
        },
    )
    response = _get_response(result)
    out_key = next(k for k in response if "country-out" in k)
    assert response[out_key]["children"] == "All: Japan, Germany, France"


# ---------------------------------------------------------------------------
# Initial values: prevent_initial_call vs. initial-callback overrides
# ---------------------------------------------------------------------------


def test_mcpb015_prevent_initial_call_uses_layout_default(dash_duo):
    """prevent_initial_call=True: initial value stays as the layout default."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dd", options=["a", "b", "c"], value="a"),
            html.Div(id="out", children="not yet"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("dd", "value"),
        prevent_initial_call=True,
    )
    def update(val):
        return f"Changed to: {val}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "not yet")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "update")
    val_desc = tool["inputSchema"]["properties"]["val"].get("description", "")

    assert "value: 'a'" in val_desc


def test_mcpb016_initial_callback_overrides_layout_value(dash_duo):
    """Initial callback overrides layout value in tool description."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="country", options=["France", "Germany"], value="France"),
            dcc.Dropdown(id="city", options=[], value="default-city"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("city", "options"),
        Output("city", "value"),
        Input("country", "value"),
    )
    def update_city(country):
        if country == "France":
            return [{"label": "Paris", "value": "Paris"}], "Paris"
        return [{"label": "Berlin", "value": "Berlin"}], "Berlin"

    @app.callback(Output("out", "children"), Input("city", "value"))
    def show_city(city):
        return f"City: {city}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "City: Paris")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "show_city")
    city_desc = tool["inputSchema"]["properties"]["city"].get("description", "")

    assert "value: 'Paris'" in city_desc
    assert "default-city" not in city_desc


def test_mcpb017_callback_context_triggered_id(dash_duo):
    """Callbacks using dash.ctx.triggered_id work via MCP.

    Based on https://dash.plotly.com/determining-which-callback-input-changed
    """
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Button 1", id="btn-1"),
            html.Button("Button 2", id="btn-2"),
            html.Button("Button 3", id="btn-3"),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("btn-1", "n_clicks"),
        Input("btn-2", "n_clicks"),
        Input("btn-3", "n_clicks"),
    )
    def display(btn1, btn2, btn3):
        if not ctx.triggered_id:
            return "No button clicked yet"
        return f"Last clicked: {ctx.triggered_id}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "No button clicked yet")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "display")
    props = tool["inputSchema"]["properties"]
    assert "btn1" in props
    assert "btn2" in props
    assert "btn3" in props

    result = _mcp_call_tool(
        dash_duo.server.url,
        "display",
        {"btn1": None, "btn2": 1, "btn3": None},
    )
    response = _get_response(result)
    assert response["output"]["children"] == "Last clicked: btn-2"

    result = _mcp_call_tool(
        dash_duo.server.url,
        "display",
        {"btn1": None, "btn2": None, "btn3": 5},
    )
    response = _get_response(result)
    assert response["output"]["children"] == "Last clicked: btn-3"


def test_mcpb018_no_output_callback_does_not_crash_tools_list(dash_duo):
    """A callback with no Output should not crash tools/list.

    No-output callbacks use set_props for side effects. They produce
    a hash-only output_id with no dot separator.
    """
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Log", id="log-btn"),
            dcc.Dropdown(id="picker", options=["a", "b"], value="a"),
            html.Div(id="display"),
        ]
    )

    @app.callback(Input("log-btn", "n_clicks"), prevent_initial_call=True)
    def log_click(n):
        set_props("display", {"children": f"Logged {n} clicks"})

    @app.callback(Output("display", "children"), Input("picker", "value"))
    def show_selection(val):
        return f"Selected: {val}"

    dash_duo.start_server(app)

    tools = _mcp_tools(dash_duo.server.url)
    tool_names = [t["name"] for t in tools]

    assert "show_selection" in tool_names
    assert "log_click" in tool_names

    result = _mcp_call_tool(
        dash_duo.server.url,
        "log_click",
        {"n": 3},
    )
    structured = result["result"]["structuredContent"]
    assert "sideUpdate" in structured
    assert structured["sideUpdate"]["display"]["children"] == "Logged 3 clicks"

    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "display", "property": "children"},
    )
    prop_info = result["result"]["structuredContent"]["properties"]["children"]
    assert "show_selection" in prop_info["modified_by_tool"]


# ---------------------------------------------------------------------------
# Duplicate outputs (allow_duplicate=True)
# ---------------------------------------------------------------------------


def test_mcpb019_duplicate_outputs_both_tools_listed(dash_duo):
    """Both callbacks outputting to the same component appear as tools."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="first-name", value="Jane"),
            dcc.Input(id="last-name", value="Doe"),
            html.Div(id="greeting"),
        ]
    )

    @app.callback(
        Output("greeting", "children"),
        Input("first-name", "value"),
    )
    def greet_by_first(first):
        return f"Hello, {first}!"

    @app.callback(
        Output("greeting", "children", allow_duplicate=True),
        Input("last-name", "value"),
        prevent_initial_call=True,
    )
    def greet_by_last(last):
        return f"Hi, {last}!"

    dash_duo.start_server(app)
    tools = _mcp_tools(dash_duo.server.url)

    first_tool = _find_tool(tools, "greet_by_first")
    last_tool = _find_tool(tools, "greet_by_last")

    assert first_tool is not None, "greet_by_first should be listed"
    assert last_tool is not None, "greet_by_last should be listed"


def test_mcpb020_duplicate_outputs_both_callable(dash_duo):
    """Both callbacks can be called and produce correct results."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="first-name", value="Jane"),
            dcc.Input(id="last-name", value="Doe"),
            html.Div(id="greeting"),
        ]
    )

    @app.callback(
        Output("greeting", "children"),
        Input("first-name", "value"),
    )
    def greet_by_first(first):
        return f"Hello, {first}!"

    @app.callback(
        Output("greeting", "children", allow_duplicate=True),
        Input("last-name", "value"),
        prevent_initial_call=True,
    )
    def greet_by_last(last):
        return f"Hi, {last}!"

    dash_duo.start_server(app)

    result1 = _mcp_call_tool(dash_duo.server.url, "greet_by_first", {"first": "Alice"})
    assert _get_response(result1)["greeting"]["children"] == "Hello, Alice!"

    result2 = _mcp_call_tool(dash_duo.server.url, "greet_by_last", {"last": "Smith"})
    assert _get_response(result2)["greeting"]["children"] == "Hi, Smith!"


def test_mcpb021_duplicate_outputs_find_by_output_returns_primary(dash_duo):
    """find_by_output returns the primary (non-duplicate) callback."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="first-name", value="Jane"),
            dcc.Input(id="last-name", value="Doe"),
            html.Div(id="greeting"),
        ]
    )

    @app.callback(
        Output("greeting", "children"),
        Input("first-name", "value"),
    )
    def greet_by_first(first):
        return f"Hello, {first}!"

    @app.callback(
        Output("greeting", "children", allow_duplicate=True),
        Input("last-name", "value"),
        prevent_initial_call=True,
    )
    def greet_by_last(last):
        return f"Hi, {last}!"

    dash_duo.start_server(app)

    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "greeting", "property": "children"},
    )
    structured = result["result"]["structuredContent"]
    assert structured["properties"]["children"]["initial_value"] == "Hello, Jane!"


# ---------------------------------------------------------------------------
# tools/list — naming rules (64-char limit, uniqueness, built-ins)
# ---------------------------------------------------------------------------


def test_mcpb022_tool_names_within_64_chars(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dd", options=["a"], value="a"),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("dd", "value"))
    def update(val):
        return val

    dash_duo.start_server(app)
    for tool in _mcp_tools(dash_duo.server.url):
        assert len(tool["name"]) <= 64, f"Tool name exceeds 64 chars: {tool['name']}"
        for param_name in tool.get("inputSchema", {}).get("properties", {}):
            assert len(param_name) <= 64, f"Param name exceeds 64 chars: {param_name}"


def test_mcpb023_long_callback_ids_within_64_chars(dash_duo):
    app = Dash(__name__)
    long_id = "a" * 120
    app.layout = html.Div(
        [
            dcc.Input(id=long_id, value="test"),
            html.Div(id=f"{long_id}-output"),
        ]
    )

    @app.callback(Output(f"{long_id}-output", "children"), Input(long_id, "value"))
    def process(val):
        return val

    dash_duo.start_server(app)
    for tool in _mcp_tools(dash_duo.server.url):
        assert len(tool["name"]) <= 64, f"Tool name exceeds 64 chars: {tool['name']}"


def test_mcpb024_pattern_matching_ids_within_64_chars(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [
                    dcc.Input(
                        id={"type": "filter-input", "index": i, "category": "primary"},
                        value=f"val-{i}",
                    )
                    for i in range(3)
                ]
            ),
            html.Div(id="pm-output"),
        ]
    )

    @app.callback(
        Output("pm-output", "children"),
        Input({"type": "filter-input", "index": 0, "category": "primary"}, "value"),
    )
    def filter_update(v0):
        return str(v0)

    dash_duo.start_server(app)
    for tool in _mcp_tools(dash_duo.server.url):
        assert len(tool["name"]) <= 64, f"Tool name exceeds 64 chars: {tool['name']}"


def test_mcpb025_duplicate_func_names_produce_unique_tools(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dd1", options=["a"], value="a"),
            html.Div(id="dd1-output"),
            dcc.Dropdown(id="dd2", options=["b"], value="b"),
            html.Div(id="dd2-output"),
            dcc.Dropdown(id="dd3", options=["c"], value="c"),
            html.Div(id="dd3-output"),
        ]
    )

    @app.callback(Output("dd1-output", "children"), Input("dd1", "value"))
    def cb(value):
        return f"first: {value}"

    @app.callback(Output("dd2-output", "children"), Input("dd2", "value"))
    def cb(value):  # noqa: F811
        return f"second: {value}"

    @app.callback(Output("dd3-output", "children"), Input("dd3", "value"))
    def cb(value):  # noqa: F811
        return f"third: {value}"

    dash_duo.start_server(app)
    tools = _mcp_tools(dash_duo.server.url)
    cb_tools = [t for t in tools if t["name"] not in ("get_dash_component",)]
    tool_names = [t["name"] for t in cb_tools]

    assert (
        len(tool_names) == 3
    ), f"Expected 3 callback tools, got {len(tool_names)}: {tool_names}"
    assert len(set(tool_names)) == 3, f"Tool names not unique: {tool_names}"


def test_mcpb026_builtin_tools_always_present(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(id="root")

    dash_duo.start_server(app)
    tool_names = [t["name"] for t in _mcp_tools(dash_duo.server.url)]
    assert "get_dash_component" in tool_names


# ---------------------------------------------------------------------------
# Input schema smoke test + get_dash_component HTTP structured output
# ---------------------------------------------------------------------------


def test_mcpb027_mcp_tool_with_label_and_date_picker_schema(dash_duo):
    """Full assertion on a tool with an html.Label and DatePickerSingle constraints."""
    label_text = "Departure Date"
    component_id = "dp"
    min_date = "2020-01-01"
    max_date = "2025-12-31"
    default_date = "2024-06-15"
    func_name = "select_date"
    param_name = "date"  # function parameter name

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label(label_text, htmlFor=component_id),
            dcc.DatePickerSingle(
                id=component_id,
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                date=default_date,
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input(component_id, "date"))
    def select_date(date):
        return f"Selected: {date}"

    dash_duo.start_server(app)
    tools = _mcp_tools(dash_duo.server.url)

    tool = next(t for t in tools if t["name"] not in ("get_dash_component",))

    assert func_name in tool["name"]

    schema = tool["inputSchema"]
    assert schema["type"] == "object"
    assert param_name in schema["required"]
    assert param_name in schema["properties"]

    prop = schema["properties"][param_name]
    assert prop["type"] == "string"
    assert prop["format"] == "date"

    desc = prop["description"]
    for expected in (label_text, min_date, max_date, default_date):
        assert expected in desc, f"Expected {expected!r} in description: {desc!r}"


EXPECTED_DROPDOWN_OPTIONS = {
    "component_id": "my-dropdown",
    "component_type": "Dropdown",
    "label": None,
    "properties": {
        "options": {
            "initial_value": [
                {"label": "New York", "value": "NYC"},
                {"label": "Montreal", "value": "MTL"},
            ],
            "modified_by_tool": [],
            "input_to_tool": [],
        },
    },
}


def test_mcpb028_query_component_returns_structured_output(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="my-dropdown",
                options=[
                    {"label": "New York", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                ],
                value="NYC",
            ),
        ]
    )

    dash_duo.start_server(app)

    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "my-dropdown", "property": "options"},
    )

    assert "result" in result, f"Expected result in response: {result}"
    structured = result["result"]["structuredContent"]
    assert structured["component_id"] == EXPECTED_DROPDOWN_OPTIONS["component_id"]
    assert structured["component_type"] == EXPECTED_DROPDOWN_OPTIONS["component_type"]
    assert (
        structured["properties"]["options"]
        == EXPECTED_DROPDOWN_OPTIONS["properties"]["options"]
    )
