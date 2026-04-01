"""
Integration tests for all Dash callback signature types.

Each test verifies that:
1. The MCP tool schema accurately reflects the callback's parameters
2. Calling the tool with those parameters produces the expected result

Assertions are derived from the callback definition, not the implementation.

See: https://dash.plotly.com/flexible-callback-signatures
"""

from dash import Dash, Input, Output, State, dcc, html

from tests.integration.mcp.conftest import _mcp_call_tool, _mcp_tools


def _find_tool(tools, name):
    return next(t for t in tools if t["name"] == name)


def _get_response(result):
    return result["result"]["structuredContent"]["response"]


def test_positional_callback(dash_duo):
    """Standard positional: Input("fruit", "value") → param named 'value'."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="fruit", options=["apple", "banana"], value="apple"),
            html.Div(id="out"),
        ]
    )

    # Callback: 1 Input → 1 param named "value" (from function signature)
    # Returns string → Output("out", "children")
    @app.callback(Output("out", "children"), Input("fruit", "value"))
    def show_fruit(value):
        return f"Selected: {value}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "Selected: apple")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "show_fruit")
    props = tool["inputSchema"]["properties"]

    assert set(props.keys()) == {"value"}
    assert any(s.get("type") == "string" for s in props["value"]["anyOf"])

    # Tool description reflects initial state
    value_desc = props["value"].get("description", "")
    assert "value: 'apple'" in value_desc
    assert "options: ['apple', 'banana']" in value_desc

    # MCP tool with initial inputs matches browser
    result = _mcp_call_tool(dash_duo.server.url, "show_fruit", {"value": "apple"})
    response = _get_response(result)
    assert response["out"]["children"] == "Selected: apple"

    # MCP tool with different inputs
    result = _mcp_call_tool(dash_duo.server.url, "show_fruit", {"value": "banana"})
    response = _get_response(result)
    assert response["out"]["children"] == "Selected: banana"


def test_positional_with_state(dash_duo):
    """Positional with State: Input + State both appear as params."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            dcc.Input(id="inp", value="hello"),
            html.Div(id="out"),
        ]
    )

    # Callback: 1 Input + 1 State → 2 params named "n_clicks" and "value"
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

    # Tool description reflects initial state
    assert "value: 'hello'" in props["value"].get("description", "")

    # MCP tool with initial inputs matches browser
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


def test_multi_output_positional(dash_duo):
    """Multi-output: returns tuple → both outputs updated in response."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="inp", value="test"),
            html.Div(id="out1"),
            html.Div(id="out2"),
        ]
    )

    # Callback: 1 Input → 2 Outputs via tuple return
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

    # Tool description reflects initial state
    assert "value: 'test'" in props["value"].get("description", "")

    # MCP tool with initial inputs matches browser
    result = _mcp_call_tool(dash_duo.server.url, "split_case", {"value": "test"})
    response = _get_response(result)
    assert response["out1"]["children"] == "TEST"
    assert response["out2"]["children"] == "test"


def test_dict_based_inputs_and_state(dash_duo):
    """Dict-based: inputs=dict(trigger=...), state=dict(name=...) → dict keys are param names."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            dcc.Input(id="name-input", value="world"),
            html.Div(id="out"),
        ]
    )

    # Callback: dict keys "trigger" and "name" become param names
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

    # MCP tool with initial inputs matches browser
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


def test_dict_based_outputs(dash_duo):
    """Dict-based outputs: output=dict(...) → callback returns dict, both outputs updated."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="inp", value="hello"),
            html.Div(id="upper-out"),
            html.Div(id="lower-out"),
        ]
    )

    # Callback: dict output keys "upper" and "lower" map to components
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

    # MCP tool with initial inputs matches browser
    result = _mcp_call_tool(dash_duo.server.url, "transform", {"val": "hello"})
    response = _get_response(result)
    assert response["upper-out"]["children"] == "HELLO"
    assert response["lower-out"]["children"] == "hello"


def test_mixed_input_state_in_inputs(dash_duo):
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

    # Callback: Input and State mixed in same dict → all keys are params
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

    # MCP tool with initial inputs matches browser
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


def test_tuple_grouped_inputs(dash_duo):
    """Tuple grouping: pair=(Input("a",...), Input("b",...)) → expands to two named params."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="a", value="1"),
            dcc.Input(id="b", value="2"),
            html.Div(id="out"),
        ]
    )

    # Callback: tuple group "pair" maps to 2 deps → 2 params named pair_<id>__<prop>
    @app.callback(
        Output("out", "children"),
        inputs=dict(pair=(Input("a", "value"), Input("b", "value"))),
    )
    def combine(pair):
        return f"{pair[0]}+{pair[1]}"

    dash_duo.start_server(app)
    tool = _find_tool(_mcp_tools(dash_duo.server.url), "combine")
    props = tool["inputSchema"]["properties"]

    # Tuple expands: one param per dep, named with group prefix + component info
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


def test_initial_values_from_chained_callbacks(dash_duo):
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

    # Tool descriptions should reflect post-initial-callback state
    tools = _mcp_tools(dash_duo.server.url)
    update_cities_tool = _find_tool(tools, "update_cities")
    state_desc = update_cities_tool["inputSchema"]["properties"]["state"].get(
        "description", ""
    )
    # state.value was set to "Ile-de-France" by update_states initial callback
    assert "Ile-de-France" in state_desc

    # state.value should be "Ile-de-France" (first state for France)
    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "state", "property": "value"},
    )
    state_props = result["result"]["structuredContent"]["properties"]
    assert state_props["value"]["initial_value"] == "Ile-de-France"

    # city.value should be "Paris" (first city for Ile-de-France)
    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "city", "property": "value"},
    )
    city_props = result["result"]["structuredContent"]["properties"]
    assert city_props["value"]["initial_value"] == "Paris"


def test_dict_based_reordered_state_input(dash_duo):
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

    # First: verify the callback actually works with these args
    result = _mcp_call_tool(
        dash_duo.server.url,
        "greet",
        {"name": "Dash", "trigger": 1},
    )
    assert _get_response(result)["out"]["children"] == "Hello Dash"

    # Second: verify schema types match annotations
    tool = _find_tool(_mcp_tools(dash_duo.server.url), "greet")
    props = tool["inputSchema"]["properties"]
    assert props["trigger"]["type"] == "integer"
    assert props["name"]["type"] == "string"

    # Third: verify each param describes the correct component
    trigger_desc = props["trigger"].get("description", "")
    assert "number of times that this element has been clicked on" in trigger_desc
    name_desc = props["name"].get("description", "")
    assert "The value of the input" in name_desc


def test_pattern_matching_callback(dash_duo):
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

    # Verify initial output matches what the browser shows
    dash_duo.wait_for_text_to_equal("#out", "hello world")
    result = _mcp_call_tool(
        dash_duo.server.url,
        "combine",
        {"first": "hello", "second": "world"},
    )
    response = _get_response(result)
    assert response["out"]["children"] == "hello world"

    # Verify with different values
    result = _mcp_call_tool(
        dash_duo.server.url,
        "combine",
        {"first": "foo", "second": "bar"},
    )
    response = _get_response(result)
    assert response["out"]["children"] == "foo bar"


def test_pattern_matching_with_all_wildcard(dash_duo):
    """ALL wildcard: one callback receives values from all matching components."""
    from dash import ALL

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

    # Schema must describe values as an array of {id, property, value} objects
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

    # MCP tool call with browser-like format: concrete IDs + values
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

    # Different values
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


def test_pattern_matching_mixed_outputs(dash_duo):
    """Mixed outputs: one regular + one ALL wildcard in the same callback."""
    from dash import ALL

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


def test_pattern_matching_with_match_wildcard(dash_duo):
    """MATCH wildcard: callback fires per-component with matching index.

    Based on https://dash.plotly.com/pattern-matching-callbacks
    """
    from dash import MATCH

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

    # Schema describes MATCH input
    value_schema = tool["inputSchema"]["properties"]["value"]
    assert "Pattern-matching input (MATCH)" in value_schema.get("description", "")

    # Call with concrete ID for index 0 (MATCH takes a single entry, not an array)
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
    # Find the output key containing "city-out" (Dash may serialize dict IDs differently)
    out_key = next(k for k in response if "city-out" in k)
    assert response[out_key]["children"] == "Selected: MTL"


def test_pattern_matching_with_allsmaller_wildcard(dash_duo):
    """ALLSMALLER wildcard: receives values from components with smaller index.

    Based on https://dash.plotly.com/pattern-matching-callbacks
    """
    from dash import MATCH, ALLSMALLER

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

    # Schema describes both MATCH and ALLSMALLER inputs
    props = tool["inputSchema"]["properties"]
    assert "Pattern-matching input (MATCH)" in props["current"].get("description", "")
    assert "Pattern-matching input (ALLSMALLER)" in props["previous"].get(
        "description", ""
    )

    # Call for index 2: MATCH is a single dict, ALLSMALLER is a list
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


def test_prevent_initial_call_uses_layout_default(dash_duo):
    """prevent_initial_call=True: initial value stays as the layout default.

    The dropdown has value="original" in the layout. The callback has
    prevent_initial_call=True so it doesn't run on page load. The MCP
    tool description should show value: 'a' (layout default).
    """
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
    # Browser shows layout default — callback hasn't fired
    dash_duo.wait_for_text_to_equal("#out", "not yet")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "update")
    val_desc = tool["inputSchema"]["properties"]["val"].get("description", "")

    # Tool description reflects layout default, not callback output
    assert "value: 'a'" in val_desc


def test_initial_callback_overrides_layout_value(dash_duo):
    """Initial callback overrides layout value in tool description.

    The city dropdown has value="default-city" in the layout.
    update_city runs on page load (no prevent_initial_call) and
    sets city.value to "Paris". The MCP tool should show "Paris"
    as the default, not "default-city".
    """
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
    # Browser shows "Paris" — the initial callback overrode "default-city"
    dash_duo.wait_for_text_to_equal("#out", "City: Paris")

    tool = _find_tool(_mcp_tools(dash_duo.server.url), "show_city")
    city_desc = tool["inputSchema"]["properties"]["city"].get("description", "")

    # Tool description should show the post-initial-callback value
    assert "value: 'Paris'" in city_desc
    assert "default-city" not in city_desc


def test_callback_context_triggered_id(dash_duo):
    """Callbacks using dash.ctx.triggered_id work via MCP.

    Based on https://dash.plotly.com/determining-which-callback-input-changed
    """
    from dash import ctx

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

    # Browser initial state: no button clicked
    dash_duo.wait_for_text_to_equal("#output", "No button clicked yet")

    # Tool should have all three button params
    tool = _find_tool(_mcp_tools(dash_duo.server.url), "display")
    props = tool["inputSchema"]["properties"]
    assert "btn1" in props
    assert "btn2" in props
    assert "btn3" in props

    # Click btn-2 via MCP — ctx.triggered_id should be "btn-2"
    result = _mcp_call_tool(
        dash_duo.server.url,
        "display",
        {"btn1": None, "btn2": 1, "btn3": None},
    )
    response = _get_response(result)
    assert response["output"]["children"] == "Last clicked: btn-2"

    # Click btn-3 via MCP
    result = _mcp_call_tool(
        dash_duo.server.url,
        "display",
        {"btn1": None, "btn2": None, "btn3": 5},
    )
    response = _get_response(result)
    assert response["output"]["children"] == "Last clicked: btn-3"


def test_no_output_callback_does_not_crash_tools_list(dash_duo):
    """A callback with no Output should not crash tools/list.

    No-output callbacks use set_props for side effects. They produce
    a hash-only output_id with no dot separator.
    """
    from dash import set_props

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

    # show_selection should appear as a tool
    assert "show_selection" in tool_names

    # log_click has no declared output but uses set_props — still a valid tool
    assert "log_click" in tool_names

    # Call log_click — sideUpdate should show the set_props effect
    result = _mcp_call_tool(
        dash_duo.server.url,
        "log_click",
        {"n": 3},
    )
    structured = result["result"]["structuredContent"]
    assert "sideUpdate" in structured
    assert structured["sideUpdate"]["display"]["children"] == "Logged 3 clicks"

    # get_dash_component shows show_selection as modifier (declared output).
    # log_click uses set_props which bypasses the declarative graph —
    # its effect is only visible via sideUpdate in tool call results.
    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "display", "property": "children"},
    )
    prop_info = result["result"]["structuredContent"]["properties"]["children"]
    assert "show_selection" in prop_info["modified_by_tool"]
