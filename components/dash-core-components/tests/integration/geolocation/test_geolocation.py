import time
from dash import Dash, dcc, html, Input, Output


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
    )
    def display_output(pos):
        if pos:
            return (
                f"lat {pos['lat']},lon {pos['lon']}, accuracy {pos['accuracy']} meters"
            )
        else:
            return "No position data available"

    dash_dcc.start_server(app)

    time.sleep(1)

    dash_dcc.wait_for_text_to_equal(
        "#text_position", "lat 45.527,lon -73.5968, accuracy 100 meters"
    )

    assert dash_dcc.get_logs() == []
