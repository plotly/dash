import time
import os
import pytest
from dash import Dash, dcc, html, Input, Output


@pytest.mark.skipif(
    os.getenv("CIRCLECI") is not None, reason="geolocation is disabled on CI"
)
def test_geol001_position(dash_dcc):
    dash_dcc.driver.execute_cdp_cmd(
        "Emulation.setGeolocationOverride",
        {"latitude": 45.527, "longitude": -73.5968, "accuracy": 100},
    )

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Geolocation(id="geolocation"),
            html.Div(id="text_position"),
        ]
    )

    @app.callback(
        Output("text_position", "children"),
        Input("geolocation", "position"),
        Input("geolocation", "position_error"),
    )
    def display_output(pos, err):
        if err:
            return f"Error {err['code']} : {err['message']}"
        if pos:
            return (
                f"lat {pos['lat']},lon {pos['lon']}, accuracy {pos['accuracy']} meters"
            )
        return "No position data available"

    dash_dcc.start_server(app)

    time.sleep(1)

    dash_dcc.wait_for_text_to_equal(
        "#text_position", "lat 45.527,lon -73.5968, accuracy 100 meters"
    )

    assert dash_dcc.get_logs() == []
