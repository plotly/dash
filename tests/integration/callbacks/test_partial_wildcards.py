from dash import Dash, Input, Output, State, ALL, html, dcc


def test_pmcb001_partial_match_basic(dash_duo):
    """Partial=True on Input matches components with extra keys."""
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            html.Button(
                "Button A",
                id={"type": "btn", "index": 1, "page": "home"},
            ),
            html.Button(
                "Button B",
                id={"type": "btn", "index": 2, "page": "settings"},
            ),
            html.Div("initial", id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input({"type": "btn"}, "n_clicks", partial=True),
        prevent_initial_call=True,
    )
    def on_click(n_clicks_list):
        total = sum(c or 0 for c in n_clicks_list)
        return f"total clicks: {total}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "initial")

    dash_duo.find_element('[id=\'{"index":1,"page":"home","type":"btn"}\']').click()
    dash_duo.wait_for_text_to_equal("#output", "total clicks: 1")

    assert dash_duo.get_logs() == []


def test_pmcb002_partial_match_all(dash_duo):
    """Partial=True with ALL collects all matching components."""
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            html.Button(
                "Btn 1",
                id={"type": "btn", "index": 1, "section": "alpha"},
            ),
            html.Button(
                "Btn 2",
                id={"type": "btn", "index": 2, "section": "beta"},
            ),
            html.Button(
                "Btn 3",
                id={"type": "other", "index": 3, "section": "gamma"},
            ),
            html.Div("initial", id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input({"type": ALL}, "n_clicks", partial=True),
    )
    def on_click(n_clicks_list):
        return f"clicks: {n_clicks_list}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "clicks: [None, None, None]")

    dash_duo.find_element('[id=\'{"index":1,"section":"alpha","type":"btn"}\']').click()
    dash_duo.wait_for_text_to_equal("#output", "clicks: [1, None, None]")

    assert dash_duo.get_logs() == []


def test_pmcb003_partial_match_literal_filter(dash_duo):
    """Partial matching with a literal value filters to specific matches."""
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            html.Button(
                "Btn A",
                id={"type": "btn", "index": 1, "page": "home"},
            ),
            html.Button(
                "Btn B",
                id={"type": "btn", "index": 2, "page": "settings"},
            ),
            html.Button(
                "Other",
                id={"type": "link", "index": 3, "page": "home"},
            ),
            html.Div("initial", id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input({"type": "btn"}, "n_clicks", partial=True),
        prevent_initial_call=True,
    )
    def on_btn_click(n_clicks_list):
        total = sum(c or 0 for c in n_clicks_list)
        return f"btn total: {total}, count: {len(n_clicks_list)}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "initial")

    dash_duo.find_element('[id=\'{"index":1,"page":"home","type":"btn"}\']').click()
    dash_duo.wait_for_text_to_equal("#output", "btn total: 1, count: 2")

    assert dash_duo.get_logs() == []


def test_pmcb004_partial_match_mixed_keys(dash_duo):
    """Components with different extra keys match the same partial pattern."""
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            html.Button(
                "A",
                id={"type": "action", "index": 1},
            ),
            html.Button(
                "B",
                id={"type": "action", "page": "main", "tab": "first"},
            ),
            html.Div("none", id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input({"type": "action"}, "n_clicks", partial=True),
        prevent_initial_call=True,
    )
    def on_action(n_clicks_list):
        total = sum(c or 0 for c in n_clicks_list)
        return f"actions: {len(n_clicks_list)}, total: {total}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", "none")

    # Click first button
    dash_duo.find_element('[id=\'{"index":1,"type":"action"}\']').click()
    dash_duo.wait_for_text_to_equal("#output", "actions: 2, total: 1")

    assert dash_duo.get_logs() == []


def test_pmcb005_partial_state(dash_duo):
    """Partial=True on State reads values from components with extra keys."""
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            dcc.Input(
                id={"type": "field", "index": 1, "form": "login"},
                value="alice",
            ),
            dcc.Input(
                id={"type": "field", "index": 2, "form": "signup"},
                value="bob",
            ),
            html.Button("Submit", id="btn", n_clicks=0),
            html.Div("waiting", id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("btn", "n_clicks"),
        State({"type": "field"}, "value", partial=True),
        prevent_initial_call=True,
    )
    def on_submit(n, values):
        return f"values: {values}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", "waiting")

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "values: ['alice', 'bob']")

    assert dash_duo.get_logs() == []


def test_pmcb006_partial_output(dash_duo):
    """Partial=True on Output writes to components with extra keys."""
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            html.Button("Go", id="btn", n_clicks=0),
            html.Div(
                "empty",
                id={"type": "display", "index": 1, "page": "home"},
            ),
            html.Div(
                "empty",
                id={"type": "display", "index": 2, "page": "settings"},
            ),
        ]
    )

    @app.callback(
        Output({"type": "display"}, "children", partial=True),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(n):
        return [f"updated-{n}"] * 2

    dash_duo.start_server(app)

    sel1 = '[id=\'{"index":1,"page":"home","type":"display"}\']'
    sel2 = '[id=\'{"index":2,"page":"settings","type":"display"}\']'

    dash_duo.wait_for_text_to_equal(sel1, "empty")
    dash_duo.wait_for_text_to_equal(sel2, "empty")

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal(sel1, "updated-1")
    dash_duo.wait_for_text_to_equal(sel2, "updated-1")

    assert dash_duo.get_logs() == []
