import dash
from dash import Dash, dcc, html


import os
import requests


def test_process_server_smoke(dash_process_server):
    cwd = os.getcwd()
    this_dir = os.path.dirname(__file__)
    assets_dir = os.path.abspath(os.path.join(this_dir, "..", "assets"))
    try:
        os.chdir(assets_dir)
        dash_process_server("simple_app")
        r = requests.get(dash_process_server.url)
        assert r.status_code == 200, "the server is reachable"
        assert 'id="react-entry-point"' in r.text, "the entrypoint is present"
    finally:
        os.chdir(cwd)


def test_paor001_order(dash_br, dash_process_server):

    app = Dash(__name__, use_pages=True)

    dash_process_server("simple_app")
    # dash_br.start_server(app)

    dash.register_page(
        "multi_layout1",
        layout=html.Div("text for multi_layout1", id="text_multi_layout1"),
        order=2,
        id="multi_layout1",
    )
    dash.register_page(
        "multi_layout2",
        layout=html.Div("text for multi_layout2", id="text_multi_layout2"),
        order=1,
        id="multi_layout2",
    )
    dash.register_page(
        "multi_layout3",
        layout=html.Div("text for multi_layout3", id="text_multi_layout3"),
        order=0,
        id="multi_layout3",
    )

    app.layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        dcc.Link(
                            f"{page['name']} - {page['path']}",
                            id=page["id"],
                            href=page["path"],
                        )
                    )
                    for page in dash.page_registry.values()
                ]
            ),
            dash.page_container,
        ]
    )

    modules = [
        "multi_layout3",
        "multi_layout2",
        "multi_layout1",
        "pages.defaults",
        "pages.metas",
        "pages.not_found_404",
        "pages.query_string",
        "pages.redirect",
    ]
    assert (
        list(dash.page_registry) == modules
    ), "check order of modules in dash.page_registry"

    dash_br.server_url = "http://localhost:8050/"
    dash_br.wait_for_text_to_equal("#out", "The first")

    assert dash_br.get_logs() == [], "browser console should contain no error"
    # dash_duo.percy_snapshot("paor001_order")
