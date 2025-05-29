import requests

from dash import Dash, html, register_page

injection_script = "<scRipt>console.error(0x000F45)</scRipt>"


def test_sinj001_url_injection(dash_duo):
    app = Dash(__name__, use_pages=True, pages_folder="")

    register_page(
        "injected",
        layout=html.Div("Regular page"),
        title="Title",
        description="desc",
        name="injected",
        path="/injected",
    )

    dash_duo.start_server(app)

    url = f"{dash_duo.server_url}/?'\"--></style></scRipt>{injection_script}"
    dash_duo.server_url = url

    assert dash_duo.get_logs() == []

    ret = requests.get(url)

    assert injection_script not in ret.text
