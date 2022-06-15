from multiprocessing import Value
from selenium.webdriver.common.keys import Keys
from dash.testing import wait
from dash import Dash, Input, Output, dcc, html


def test_link001_event(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Link("Page 1", id="link1", href="/page-1"),
            dcc.Location(id="url", refresh=False),
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

    dash_dcc.find_element("#link1").click()

    dash_dcc.wait_for_element_by_id("div1")

    link_counter = dash_dcc.driver.execute_script(
        """
        return window._test_link_event_counter;
    """
    )

    history_counter = dash_dcc.driver.execute_script(
        """
        return window._test_history_event_counter;
    """
    )

    assert link_counter == 1
    assert history_counter == 1

    assert dash_dcc.get_logs() == []


def test_link002_scroll(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Location(id="test-url", refresh=False),
            html.Div(
                id="push-to-bottom",
                children=[],
                style={"display": "block", "height": "200vh"},
            ),
            html.Div(id="page-content"),
            dcc.Link("Test link", href="/test-link", id="test-link"),
        ]
    )

    call_count = Value("i", 0)

    @app.callback(Output("page-content", "children"), [Input("test-url", "pathname")])
    def display_page(pathname):
        call_count.value = call_count.value + 1
        return f"You are on page {pathname}"

    dash_dcc.start_server(app)

    wait.until(lambda: call_count.value == 1, 3)

    test_link = dash_dcc.wait_for_element("#test-link")
    test_link.send_keys(Keys.NULL)
    test_link.click()

    dash_dcc.wait_for_text_to_equal("#page-content", "You are on page /test-link")

    wait.until(
        lambda: test_link.get_attribute("href")
        == f"http://localhost:{dash_dcc.server.port}/test-link",
        3,
    )
    wait.until(lambda: call_count.value == 2, 3)

    assert dash_dcc.get_logs() == []
