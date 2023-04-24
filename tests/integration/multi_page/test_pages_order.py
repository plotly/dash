import dash
from dash import Dash, dcc, html


def test_paor001_order(dash_duo, clear_pages_state):

    app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

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
            dcc.Location(id="url", refresh=True),
        ]
    )

    modules = [
        "multi_layout3",
        "multi_layout2",
        "multi_layout1",
        "pages.defaults",
        "pages.metas",
        "pages.not_found_404",
        "pages.page1",
        "pages.page2",
        "pages.path_variables",
        "pages.query_string",
        "pages.redirect",
    ]

    dash_duo.start_server(app)

    assert (
        list(dash.page_registry) == modules
    ), "check order of modules in dash.page_registry"

    # There should be no `validation_layout` when suppress_callback_exceptions=True`
    assert app.validation_layout is None

    assert dash_duo.get_logs() == [], "browser console should contain no error"
