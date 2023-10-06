import pytest
import dash
from dash import Dash, Input, State, dcc, html
from dash.dash import _ID_LOCATION
from dash.exceptions import NoLayoutException


def get_app(path1="/", path2="/layout2"):
    app = Dash(__name__, use_pages=True)

    # test for storing arbitrary keyword arguments: An `id` prop is defined for every page
    # test for defining multiple pages within a single file: layout is passed directly to `register_page`
    # in the following two modules:
    dash.register_page(
        "multi_layout1",
        layout=html.Div("text for multi_layout1", id="text_multi_layout1"),
        path=path1,
        title="Supplied Title",
        description="This is the supplied description",
        name="Supplied name",
        image="birds.jpeg",
        id="multi_layout1",
    )
    dash.register_page(
        "multi_layout2",
        layout=html.Div("text for multi_layout2", id="text_multi_layout2"),
        path=path2,
        id="multi_layout2",
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
    return app


def test_pala001_layout(dash_duo, clear_pages_state):
    app = get_app()
    dash_duo.start_server(app)

    # test layout and title for each page in `page_registry` with link navigation
    for page in dash.page_registry.values():
        dash_duo.find_element("#" + page["id"]).click()
        dash_duo.wait_for_text_to_equal("#text_" + page["id"], "text for " + page["id"])
        assert dash_duo.driver.title == page["title"], "check that page title updates"

    # test redirects
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/v2")
    dash_duo.wait_for_text_to_equal("#text_redirect", "text for redirect")
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/old-home-page")
    dash_duo.wait_for_text_to_equal("#text_redirect", "text for redirect")
    assert dash_duo.driver.current_url == f"{dash_duo.server_url}/redirect"

    # test redirect with button and user defined dcc.Location
    # note:  dcc.Location must be defined in app.py
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/page1")
    dash_duo.find_element("#btn1").click()
    dash_duo.wait_for_text_to_equal("#text_page2", "text for page2")

    # test query strings
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/query-string?velocity=10")
    assert (
        dash_duo.find_element("#velocity").get_attribute("value") == "10"
    ), "query string passed to layout"

    # test path variables
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/a/none/b/none")
    dash_duo.wait_for_text_to_equal("#path_vars", "variables from pathname:none none")

    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/a/var1/b/var2")
    dash_duo.wait_for_text_to_equal("#path_vars", "variables from pathname:var1 var2")

    # test page not found
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/find_me")
    dash_duo.wait_for_text_to_equal("#text_not_found_404", "text for not_found_404")

    # test `validation_layout` exists when suppress_callback_exceptions=False`
    assert app.validation_layout is not None

    assert dash_duo.get_logs() == [], "browser console should contain no error"
    # dash_duo.percy_snapshot("pala001_layout")


def check_metas(dash_duo, metas):
    meta = dash_duo.find_elements("meta")

    # -3 for the meta charset and http-equiv and viewport.
    assert len(meta) == len(metas) + 3, "Should have  extra meta tags"

    assert meta[0].get_attribute("name") == metas[0]["name"]
    assert meta[0].get_attribute("content") == metas[0]["content"]
    for i in range(1, len(meta) - 3):
        assert meta[i].get_attribute("property") == metas[i]["property"]
        assert meta[i].get_attribute("content") == metas[i]["content"]


def test_pala002_meta_tags_default(dash_duo, clear_pages_state):
    dash_duo.start_server(get_app(path1="/layout1", path2="/"))
    # These are the inferred defaults if description, title, image are not supplied
    metas_layout2 = [
        {"name": "description", "content": ""},
        {"property": "twitter:card", "content": "summary_large_image"},
        {
            "property": "twitter:url",
            "content": f"{dash_duo.server_url}/",
        },
        {"property": "twitter:title", "content": "Multi layout2"},
        {"property": "twitter:description", "content": ""},
        {
            "property": "twitter:image",
            "content": f"{dash_duo.server_url}/assets/app.jpeg",
        },
        {"property": "og:title", "content": "Multi layout2"},
        {"property": "og:type", "content": "website"},
        {"property": "og:description", "content": ""},
        {
            "property": "og:image",
            "content": f"{dash_duo.server_url}/assets/app.jpeg",
        },
    ]

    check_metas(dash_duo, metas_layout2)


def test_pala003_meta_tags_custom(dash_duo, clear_pages_state):
    dash_duo.start_server(get_app())
    # In the "multi_layout1" module, the description, title, image are supplied
    metas_layout1 = [
        {"name": "description", "content": "This is the supplied description"},
        {"property": "twitter:card", "content": "summary_large_image"},
        {
            "property": "twitter:url",
            "content": f"{dash_duo.server_url}/",
        },
        {"property": "twitter:title", "content": "Supplied Title"},
        {
            "property": "twitter:description",
            "content": "This is the supplied description",
        },
        {
            "property": "twitter:image",
            "content": f"{dash_duo.server_url}/assets/birds.jpeg",
        },
        {"property": "og:title", "content": "Supplied Title"},
        {"property": "og:type", "content": "website"},
        {"property": "og:description", "content": "This is the supplied description"},
        {
            "property": "og:image",
            "content": f"{dash_duo.server_url}/assets/birds.jpeg",
        },
    ]

    check_metas(dash_duo, metas_layout1)


def test_pala004_no_layout_exception(clear_pages_state):
    error_msg = 'No layout found in module pages_error.no_layout_page\nA variable or a function named "layout" is required.'

    with pytest.raises(NoLayoutException) as err:
        Dash(__name__, use_pages=True, pages_folder="pages_error")

    assert error_msg in err.value.args[0]


def get_routing_inputs_app():
    app = Dash(
        __name__,
        use_pages=True,
        routing_callback_inputs={
            "hash": State(_ID_LOCATION, "hash"),
            "language": Input("language", "value"),
        },
    )
    # Page with layout from a variable: should render and not be impacted
    # by routing callback inputs
    dash.register_page(
        "home",
        layout=html.Div("Home", id="contents"),
        path="/",
    )

    # Page with a layout function, should see the routing callback inputs
    # as keyword arguments
    def layout1(hash: str = None, language: str = "en", **kwargs):
        translations = {
            "en": "Hash says: {}",
            "fr": "Le hash dit: {}",
        }
        return html.Div(translations[language].format(hash), id="contents")

    dash.register_page(
        "function_layout",
        path="/function-layout",
        layout=layout1,
    )
    app.layout = html.Div(
        [
            dcc.Dropdown(id="language", options=["en", "fr"], value="en"),
            dash.page_container,
        ]
    )
    return app


def test_pala005_routing_inputs(dash_duo, clear_pages_state):
    dash_duo.start_server(get_routing_inputs_app())
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}#123")
    dash_duo.wait_for_text_to_equal("#contents", "Home")
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/")
    dash_duo.wait_for_text_to_equal("#contents", "Home")
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/function-layout")
    dash_duo.wait_for_text_to_equal("#contents", "Hash says:")
    # hash is a State therefore navigating to the same page with hash will not
    # re-render the layout function
    dash_duo.wait_for_page(url=f"{dash_duo.server_url}/function-layout#123")
    dash_duo.wait_for_text_to_equal("#contents", "Hash says:")
    # Refreshing the page re-runs the layout function
    dash_duo.driver.refresh()
    dash_duo.wait_for_text_to_equal("#contents", "Hash says: #123")
    # Changing the language Input re-runs the layout function
    dash_duo.select_dcc_dropdown("#language", "fr")
    dash_duo.wait_for_text_to_equal("#contents", "Le hash dit: #123")
