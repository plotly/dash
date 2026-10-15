import time

from dash import Dash, Input, Output, dcc, html
from dash.testing.wait import until


def test_callback_returning_none_removes_child_paths_and_can_remount(dash_duo):
    view_calls = []

    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Button("Toggle", id="toggle"),
            dcc.Interval(id="tick", interval=200),
            html.Div(id="container"),
        ]
    )

    @app.callback(
        Output("container", "children"),
        Input("toggle", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_view(n_clicks):
        if n_clicks % 2:
            return html.Div(html.Span(id="view-child"), id="view")
        return None

    @app.callback(Output("view-child", "children"), Input("tick", "n_intervals"))
    def update_view(n_intervals):
        view_calls.append(n_intervals)
        return f"tick {n_intervals}"

    dash_duo.start_server(app)

    dash_duo.find_element("#toggle").click()
    dash_duo.wait_for_element("#view-child")
    until(lambda: "view-child" in dash_duo.redux_state_paths["strs"], timeout=3)
    until(lambda: view_calls, timeout=3)

    dash_duo.find_element("#toggle").click()
    dash_duo.wait_for_no_elements("#view-child")
    until(lambda: "view-child" not in dash_duo.redux_state_paths["strs"], timeout=3)
    calls_after_unmount = len(view_calls)
    time.sleep(0.5)
    assert len(view_calls) == calls_after_unmount

    dash_duo.find_element("#toggle").click()
    dash_duo.wait_for_element("#view-child")
    until(lambda: "view-child" in dash_duo.redux_state_paths["strs"], timeout=3)
