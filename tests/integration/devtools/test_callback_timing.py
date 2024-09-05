from time import sleep
import requests

from dash import Dash, Output, Input, html, callback_context


def test_dvct001_callback_timing(dash_thread_server):
    app = Dash(__name__)
    app.layout = html.Div()

    @app.callback(Output("x", "p"), Input("y", "q"))
    def x(y):
        callback_context.record_timing("pancakes", 1.23)
        sleep(0.5)
        return y

    dash_thread_server(app, debug=True, use_reloader=False, use_debugger=True)

    response = requests.post(
        dash_thread_server.url + "/_dash-update-component",
        json={
            "output": "x.p",
            "outputs": {"id": "x", "property": "p"},
            "inputs": [{"id": "y", "property": "q", "value": 9}],
            "changedPropIds": ["y.q"],
        },
    )

    # eg 'Server-Timing': '__dash_server;dur=505, pancakes;dur=1230'
    assert "Server-Timing" in response.headers
    st = response.headers["Server-Timing"]
    times = {k: int(float(v)) for k, v in [p.split(";dur=") for p in st.split(", ")]}
    assert "__dash_server" in times
    assert times["__dash_server"] >= 500  # 0.5 sec wait
    assert "pancakes" in times
    assert times["pancakes"] == 1230
