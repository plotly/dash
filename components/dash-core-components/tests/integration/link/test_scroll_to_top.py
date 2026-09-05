import pytest

from dash import Dash, dcc, html
from dash.testing.wait import until


@pytest.mark.parametrize(
    "link_props,scrolls_to_top",
    [({}, True), ({"scrollToTop": False}, False)],
    ids=["default", "disabled"],
)
def test_lisc001_scroll_to_top(dash_dcc, link_props, scrolls_to_top):
    behavior = "enabled (default)" if scrolls_to_top else "disabled"
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.H1("TOP OF PAGE", id="top-marker"),
                    html.P("The default Link behavior returns here after a click."),
                ],
                id="top-section",
                style={
                    "height": "100vh",
                    "padding": "1rem",
                    "boxSizing": "border-box",
                },
            ),
            html.Div(
                [
                    html.H1("BOTTOM OF PAGE", id="bottom-marker"),
                    html.P(f"scrollToTop is {behavior}."),
                    dcc.Link(
                        "Click to navigate",
                        href="/test-link",
                        id="test-link",
                        **link_props,
                    ),
                ],
                id="bottom-section",
                style={
                    "height": "100vh",
                    "padding": "1rem",
                    "boxSizing": "border-box",
                    "borderTop": "1px solid",
                },
            ),
        ]
    )

    dash_dcc.start_server(app)

    test_link = dash_dcc.wait_for_element("#test-link")
    dash_dcc.driver.execute_script(
        "document.getElementById('bottom-section').scrollIntoView()"
    )
    until(lambda: dash_dcc.driver.execute_script("return window.scrollY") > 0, 3)
    initial_scroll_position = dash_dcc.driver.execute_script("return window.scrollY")

    test_link.click()

    until(lambda: dash_dcc.driver.current_url.endswith("/test-link"), 3)
    expected_scroll_position = 0 if scrolls_to_top else initial_scroll_position
    until(
        lambda: dash_dcc.driver.execute_script("return window.scrollY")
        == expected_scroll_position,
        3,
    )

    assert dash_dcc.get_logs() == []
