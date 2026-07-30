"""
Integration tests for callback payload compression.
"""

import pytest
from dash import Dash, html, dcc, Input, Output, State
from dash._compression import COMPRESSED_PAYLOAD_FIELD


@pytest.mark.parametrize(
    "backend,dash_duo_fixture",
    [("flask", "dash_duo"), ("quart", "dash_duo_mp"), ("fastapi", "dash_duo")],
)
@pytest.mark.parametrize("payload_size", [1, 500_000])
@pytest.mark.parametrize("compress_threshold", [0, 500_000])
def test_cbcomp01_compress_request_payload(
    request, dash_duo_fixture, backend, payload_size, compress_threshold
):
    """Test that the client sends a compressed body when appropriate."""
    if backend == "quart":
        pytest.importorskip(
            "quart", reason="Quart extra dependencies are not installed"
        )
        pytest.importorskip("hypercorn", reason="hypercorn is not installed")
    elif backend == "fastapi":
        pytest.importorskip(
            "fastapi", reason="fastapi extra dependencies are not installed"
        )

    app = Dash(__name__, backend=backend)

    # intercept the request to /_dash-update-component and record whether the payload was compressed
    if backend == "quart":
        # async capture for quart
        @app.backend.before_request
        async def capture_compression():
            request = app.backend.request_adapter()
            if request.path == "/_dash-update-component":
                body = await request.get_json() or {}
                if COMPRESSED_PAYLOAD_FIELD in body:
                    request.context.compressed_payload_size = len(
                        body[COMPRESSED_PAYLOAD_FIELD]
                    )
                else:
                    request.context.compressed_payload_size = None

    else:
        # sync capture for flask and fastapi
        @app.backend.before_request
        def capture_compression():
            request = app.backend.request_adapter()
            if request.path == "/_dash-update-component":
                body = request.get_json() or {}
                if COMPRESSED_PAYLOAD_FIELD in body:
                    request.context.compressed_payload_size = len(
                        body[COMPRESSED_PAYLOAD_FIELD]
                    )
                else:
                    request.context.compressed_payload_size = None

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
        compressed_payload_size = (
            app.backend.request_adapter().context.compressed_payload_size
        )
        return (
            len(data),
            repr(compressed_payload_size is not None),
            compressed_payload_size,
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

    dash_duo = request.getfixturevalue(dash_duo_fixture)
    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()
    # assert that the data size matches the expected payload size
    dash_duo.wait_for_text_to_equal("#data_size", f"{payload_size}")
    # assert that the data was compressed if the payload size is greater than or equal to the compression threshold
    dash_duo.wait_for_text_to_equal(
        "#data_compressed", repr(payload_size >= compress_threshold)
    )
