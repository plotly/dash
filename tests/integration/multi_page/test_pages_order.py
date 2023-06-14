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
    # Test more than 10 pages to ensure the supplied order is sorted correctly
    for order_int in range(3, 13):
        dash.register_page(
            f"multi_layout{order_int + 1}",
            layout=html.Div(
                f"text for multi_layout{order_int + 1}",
                id=f"text_multi_layout{order_int + 1}",
            ),
            order=order_int,
            id=f"multi_layout{order_int + 1}",
        )
    # Test fractional ordering
    dash.register_page(
        "multi_layout3.5",
        layout=html.Div("text for multi_layout3.5", id="text_multi_layout3.5"),
        order=3.5,
        id="multi_layout3.5",
    )
    # Test no order given
    dash.register_page(
        "multi_layout14",
        layout=html.Div("text for multi_layout14", id="text_multi_layout14"),
        id="multi_layout14",
    )
    dash.register_page(
        "multi_layout15",
        layout=html.Div("text for multi_layout15", id="text_multi_layout15"),
        id="multi_layout15",
    )
    # Test string for order
    dash.register_page(
        "first_string_order",
        layout=html.Div("text for string_order", id="text_string_order"),
        order="2a",
        id="first_string_order",
    )
    dash.register_page(
        "aaa_first_with_no_order",
        layout=html.Div("text for aaa", id="text_aaa"),
        id="aaa_first_with_no_order",
    )
    dash.register_page(
        "yyy_last_string_order",
        layout=html.Div("text for yyy", id="text_yyy"),
        order="zzz",
        id="yyy_last_string_order",
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
        "multi_layout4",
        "multi_layout3.5",
        "multi_layout5",
        "multi_layout6",
        "multi_layout7",
        "multi_layout8",
        "multi_layout9",
        "multi_layout10",
        "multi_layout11",
        "multi_layout12",
        "multi_layout13",
        "first_string_order",
        "yyy_last_string_order",
        "aaa_first_with_no_order",
        "multi_layout14",
        "multi_layout15",
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
