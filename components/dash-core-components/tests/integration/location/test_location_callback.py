import pytest
from dash import Dash, Input, Output, State, dcc, html


from dash.testing.wait import until


@pytest.mark.DCC774
def test_loca001_callbacks(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Location(id="location", refresh=False),
            html.A("Anchor Link 1", href="#div"),
            html.Div(id="div"),
        ]
    )

    @app.callback(Output("div", "children"), [Input("location", "pathname")])
    def update_path(path):
        return path

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#div", "/")

    assert dash_dcc.get_logs() == []


def test_loca002_location_link(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div(id="waitfor"),
            dcc.Location(id="test-location", refresh=False),
            dcc.Link(
                html.Button("I am a clickable button"),
                id="test-link",
                href="/test/pathname",
            ),
            dcc.Link(
                html.Button("I am a clickable hash button"),
                id="test-link-hash",
                href="#test",
            ),
            dcc.Link(
                html.Button("I am a clickable search button"),
                id="test-link-search",
                href="?testQuery=testValue",
                refresh=False,
            ),
            html.Button("I am a magic button that updates pathname", id="test-button"),
            html.A("link to click", href="/test/pathname/a", id="test-a"),
            html.A("link to click", href="#test-hash", id="test-a-hash"),
            html.A("link to click", href="?queryA=valueA", id="test-a-query"),
            html.Div(id="test-pathname", children=[]),
            html.Div(id="test-hash", children=[]),
            html.Div(id="test-search", children=[]),
        ]
    )

    @app.callback(
        Output("test-pathname", "children"), Input("test-location", "pathname")
    )
    def update_test_pathname(pathname):
        return pathname

    @app.callback(Output("test-hash", "children"), Input("test-location", "hash"))
    def update_test_hash(hash_val):
        return hash_val or ""

    @app.callback(Output("test-search", "children"), Input("test-location", "search"))
    def update_test_search(search):
        return search or ""

    @app.callback(
        Output("test-location", "pathname"),
        Input("test-button", "n_clicks"),
        State("test-location", "pathname"),
    )
    def update_pathname(n_clicks, current_pathname):
        if n_clicks is not None:
            return "/new/pathname"

        return current_pathname

    dash_dcc.start_server(app)

    def check_path_parts(pathname, search, _hash):
        dash_dcc.wait_for_text_to_equal("#test-pathname", pathname)
        dash_dcc.wait_for_text_to_equal("#test-search", search)
        dash_dcc.wait_for_text_to_equal("#test-hash", _hash)

        expected = f"http://localhost:{dash_dcc.server.port}{pathname}{search}{_hash}"
        assert dash_dcc.driver.current_url == expected

        assert dash_dcc.get_logs() == []

    check_path_parts("/", "", "")

    # Check that link updates pathname
    dash_dcc.find_element("#test-link").click()
    until(
        lambda: dash_dcc.driver.current_url.replace(
            f"http://localhost:{dash_dcc.server.port}", ""
        )
        == "/test/pathname",
        3,
    )
    check_path_parts("/test/pathname", "", "")

    # Check that hash is updated in the Location
    dash_dcc.find_element("#test-link-hash").click()
    check_path_parts("/test/pathname", "", "#test")

    # Check that search is updated in the Location
    # note that this goes through href and therefore wipes the hash
    dash_dcc.find_element("#test-link-search").click()
    check_path_parts("/test/pathname", "?testQuery=testValue", "")

    # Check that pathname is updated through a Button click via props
    dash_dcc.find_element("#test-button").click()
    check_path_parts("/new/pathname", "?testQuery=testValue", "")

    # Check that pathname is updated through an a tag click via props
    dash_dcc.find_element("#test-a").click()
    check_path_parts("/test/pathname/a", "", "")

    # Check that hash is updated through an a tag click via props
    dash_dcc.find_element("#test-a-hash").click()
    check_path_parts("/test/pathname/a", "", "#test-hash")

    # Check that hash is updated through an a tag click via props
    dash_dcc.find_element("#test-a-query").click()
    check_path_parts("/test/pathname/a", "?queryA=valueA", "")

    assert dash_dcc.get_logs() == []


def test_loca003_location_callback(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            dcc.Location(id="callback-url", refresh="callback-nav"),
            html.Button(id="callback-btn", n_clicks=0),
            html.Div(id="content"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("url", "pathname")])
    def display_page(pathname):
        if pathname is None or pathname == "/page-1":
            return html.Div("1", id="div1")
        elif pathname == "/":
            return html.Div("base", id="div0")
        else:
            return "404"

    @app.callback(
        Output("callback-url", "pathname"),
        Input("callback-btn", "n_clicks"),
    )
    def update_location(n):
        if n > 0:
            return "/page-1"

    dash_dcc.start_server(app)
    dash_dcc.driver.execute_script(
        """
        window.addEventListener('_dashprivate_pushstate', function() {
            window._test_link_event_counter = (window._test_link_event_counter || 0) + 1;
        });

        window.addEventListener('_dashprivate_historychange', function() {
            window._test_history_event_counter = (window._test_history_event_counter || 0) + 1;
        });
    """
    )

    dash_dcc.wait_for_element_by_id("div0")

    dash_dcc.find_element("#callback-btn").click()

    dash_dcc.wait_for_element_by_id("div1")

    assert dash_dcc.get_logs() == []
