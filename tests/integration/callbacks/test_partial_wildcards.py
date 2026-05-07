"""Tests for partial pattern matching in callbacks."""

import json

from dash import Dash, Input, Output, ALL, html


def stringify_id(id_):
    if isinstance(id_, dict):
        return json.dumps(id_, sort_keys=True, separators=(",", ":"))
    return id_


def test_partial_match_basic(dash_duo):
    """A callback with partial=True on Input matches components with extra keys.
    Literal-only partial patterns are implicitly multi-valued (return a list).
    """
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            # Components with extra keys beyond what the callback pattern specifies
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
        # Literal-only partial is multi-valued: receives a list
        total = sum(c or 0 for c in n_clicks_list)
        return f"total clicks: {total}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "initial")

    # Click the first button - should trigger partial match
    dash_duo.find_element('[id=\'{"index":1,"page":"home","type":"btn"}\']').click()
    dash_duo.wait_for_text_to_equal("#output", "total clicks: 1")

    assert dash_duo.get_logs() == []


def test_partial_match_all(dash_duo):
    """A callback with partial=True and ALL collects all matching components."""
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

    # Should collect all 3 buttons (all have "type" key)
    dash_duo.wait_for_text_to_equal("#output", "clicks: [None, None, None]")

    dash_duo.find_element('[id=\'{"index":1,"section":"alpha","type":"btn"}\']').click()
    dash_duo.wait_for_text_to_equal("#output", "clicks: [1, None, None]")

    assert dash_duo.get_logs() == []


def test_partial_match_with_literal_value(dash_duo):
    """Partial matching with a literal value filters to specific matches.
    Only components where type='btn' are collected (multi-valued).
    """
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
        # Only type="btn" components are collected (not type="link")
        total = sum(c or 0 for c in n_clicks_list)
        return f"btn total: {total}, count: {len(n_clicks_list)}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "initial")

    # Click a "btn" type - should trigger, collecting 2 btn components
    dash_duo.find_element('[id=\'{"index":1,"page":"home","type":"btn"}\']').click()
    dash_duo.wait_for_text_to_equal("#output", "btn total: 1, count: 2")

    assert dash_duo.get_logs() == []


def test_partial_match_mixed_keys(dash_duo):
    """Components with different extra keys all match the same partial pattern.
    Both components have type='action' but different other keys.
    """
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            # Different components with different key sets, all having "type"
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
        # Multi-valued: collects from all components with type="action"
        total = sum(c or 0 for c in n_clicks_list)
        return f"actions: {len(n_clicks_list)}, total: {total}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", "none")

    # Click first button
    dash_duo.find_element('[id=\'{"index":1,"type":"action"}\']').click()
    dash_duo.wait_for_text_to_equal("#output", "actions: 2, total: 1")

    assert dash_duo.get_logs() == []
