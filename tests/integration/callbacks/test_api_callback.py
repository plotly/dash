from dash import (
    Dash,
    Input,
    Output,
    html,
    ctx,
)
import requests
import json
from flask import jsonify

test_string = (
    '{"step_0": "Data fetched - 1", "step_1": "Data fetched - 1", "step_2": "Data fetched - 1", '
    '"step_3": "Data fetched - 1", "step_4": "Data fetched - 1"}'
)


def test_apib001_api_callback(dash_duo):

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Slow Callback", id="slow-btn"),
            html.Div(id="slow-output"),
        ]
    )

    def get_data(n_clicks):
        # Simulate an async data fetch
        return f"Data fetched - {n_clicks}"

    @app.callback(
        Output("slow-output", "children"),
        Input("slow-btn", "n_clicks"),
        prevent_initial_call=True,
        api_endpoint="/api/slow_callback",  # Example API path for the slow callback
    )
    def slow_callback(n_clicks):
        data = {}
        for i in range(5):
            data[f"step_{i}"] = get_data(n_clicks)
        ret = f"{json.dumps(data)}"
        if ctx:
            return ret
        return jsonify(ret)

    app.setup_apis()

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#slow-btn").click()
    dash_duo.wait_for_text_to_equal("#slow-output", test_string)
    r = requests.post(
        dash_duo.server_url + "/api/slow_callback",
        json={"n_clicks": 1},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200
    assert r.json() == test_string
