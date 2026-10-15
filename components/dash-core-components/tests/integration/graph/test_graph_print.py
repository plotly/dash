import base64

import pytest

from dash import Dash, dcc


@pytest.mark.parametrize("point_count", [1000, 1001])
def test_grpr001_graph_survives_print(point_count, dash_dcc):
    app = Dash(__name__)
    points = list(range(point_count))
    app.layout = dcc.Graph(
        id="graph",
        figure={
            "data": [{"type": "scatter", "mode": "lines", "x": points, "y": points}],
            "layout": {"width": 600, "height": 400},
        },
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#graph .main-svg")

    driver = dash_dcc.driver
    if not hasattr(driver, "execute_cdp_cmd"):
        pytest.skip("print-to-PDF regression requires Chrome DevTools Protocol")

    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
    pdf = driver.execute_cdp_cmd(
        "Page.printToPDF", {"printBackground": True, "preferCSSPageSize": True}
    )

    pdf_bytes = base64.b64decode(pdf["data"])
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000
    assert dash_dcc.find_element("#graph .scatterlayer .trace path").is_displayed()
    assert dash_dcc.get_logs() == []
