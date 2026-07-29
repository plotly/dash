"""
Integration tests for callback payload compression.
"""

import flask
import pytest
from dash import Dash, html, dcc, Input, Output, State
from dash._compression import COMPRESSED_PAYLOAD_FIELD


@pytest.mark.parametrize("payload_size", [1, 500_000])
@pytest.mark.parametrize("compress_threshold", [0, 500_000])
def test_cbcomp01_always_compress(dash_duo, payload_size, compress_threshold):
    """Test that the client sends a compressed body when appropriate."""
    app = Dash(__name__)

    @app.server.before_request
    def capture_compression():
        # intercept the request to /_dash-update-component and record whether the payload was compressed
        if flask.request.path == "/_dash-update-component":
            body = flask.request.get_json(silent=True) or {}
            if COMPRESSED_PAYLOAD_FIELD in body:
                flask.g.compressed_payload_size = len(body[COMPRESSED_PAYLOAD_FIELD])
            else:
                flask.g.compressed_payload_size = None

    @app.callback(
        Output("data_size", "children"),
        Output("data_compressed", "children"),
        Output("data_compressed_size", "children"),
        Input("btn", "n_clicks"),
        State("store", "data"),
        compress_payload=True,
        compress_threshold=compress_threshold,
        prevent_initial_call=True,
    )
    def on_click(n, data):
        # log the size of the data and whether it was compressed
        return (
            len(data),
            repr(flask.g.compressed_payload_size is not None),
            flask.g.compressed_payload_size,
        )

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div(id="data_size"),
            html.Div(id="data_compressed"),
            html.Div(id="data_compressed_size"),
            dcc.Store(id="store", data="x" * payload_size),
        ]
    )

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()
    # assert that the data size matches the expected payload size
    dash_duo.wait_for_text_to_equal("#data_size", f"{payload_size}")
    # assert that the data was compressed if the payload size is greater than or equal to the compression threshold
    dash_duo.wait_for_text_to_equal(
        "#data_compressed", repr(payload_size >= compress_threshold)
    )
