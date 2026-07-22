from dash import Dash, Input, Output, dcc, html
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def test_btev001_clicks_and_blur(dash_dcc):
    """Test that n_clicks, n_clicks_timestamp, n_blur, and n_blur_timestamp work correctly"""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Button(
                "Click Me",
                id="test-button",
                className="custom-button-class",
            ),
            html.Div(id="click-output"),
            html.Div(id="blur-output"),
            html.Div(id="click-timestamp-output"),
            html.Div(id="blur-timestamp-output"),
            # Add a second element to blur to
            html.Button("Other Element", id="other-element"),
        ]
    )

    @app.callback(
        Output("click-output", "children"),
        Input("test-button", "n_clicks"),
    )
    def update_clicks(n_clicks):
        if n_clicks is None:
            return "Clicks: 0"
        return f"Clicks: {n_clicks}"

    @app.callback(
        Output("blur-output", "children"),
        Input("test-button", "n_blur"),
    )
    def update_blur(n_blur):
        if n_blur is None:
            return "Blurs: 0"
        return f"Blurs: {n_blur}"

    @app.callback(
        Output("click-timestamp-output", "children"),
        Input("test-button", "n_clicks_timestamp"),
    )
    def update_click_timestamp(n_clicks_timestamp):
        if n_clicks_timestamp is None or n_clicks_timestamp == -1:
            return "Click timestamp: None"
        return f"Click timestamp: {n_clicks_timestamp}"

    @app.callback(
        Output("blur-timestamp-output", "children"),
        Input("test-button", "n_blur_timestamp"),
    )
    def update_blur_timestamp(n_blur_timestamp):
        if n_blur_timestamp is None or n_blur_timestamp == -1:
            return "Blur timestamp: None"
        return f"Blur timestamp: {n_blur_timestamp}"

    dash_dcc.start_server(app)

    # Verify custom class is applied
    button = dash_dcc.find_element(".custom-button-class")
    assert button is not None, "Custom className should be applied"

    # Check initial state
    dash_dcc.wait_for_text_to_equal("#click-output", "Clicks: 0")
    dash_dcc.wait_for_text_to_equal("#blur-output", "Blurs: 0")
    dash_dcc.wait_for_text_to_equal("#click-timestamp-output", "Click timestamp: None")
    dash_dcc.wait_for_text_to_equal("#blur-timestamp-output", "Blur timestamp: None")

    # Click the button
    button.click()
    dash_dcc.wait_for_text_to_equal("#click-output", "Clicks: 1")

    # Verify click timestamp is set
    click_timestamp_text = dash_dcc.find_element("#click-timestamp-output").text
    assert "Click timestamp: " in click_timestamp_text
    assert click_timestamp_text != "Click timestamp: None"

    # Click again
    button.click()
    dash_dcc.wait_for_text_to_equal("#click-output", "Clicks: 2")

    # Blur by clicking on other element
    other_element = dash_dcc.find_element("#other-element")
    other_element.click()

    # Check blur was registered
    dash_dcc.wait_for_text_to_equal("#blur-output", "Blurs: 1")

    # Verify blur timestamp is set
    blur_timestamp_text = dash_dcc.find_element("#blur-timestamp-output").text
    assert "Blur timestamp: " in blur_timestamp_text
    assert blur_timestamp_text != "Blur timestamp: None"

    # Click the button again to focus it
    button.click()
    dash_dcc.wait_for_text_to_equal("#click-output", "Clicks: 3")

    # Blur again by clicking other element
    other_element.click()
    dash_dcc.wait_for_text_to_equal("#blur-output", "Blurs: 2")

    assert dash_dcc.get_logs() == []


def test_btev002_disabled_button(dash_dcc):
    """Test that disabled button doesn't trigger click or blur events"""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Button(
                "Disabled Button",
                id="disabled-button",
                className="disabled-test-button",
                disabled=True,
            ),
            html.Div(id="click-output"),
            html.Div(id="blur-output"),
            html.Button("Other Element", id="other-element"),
        ]
    )

    @app.callback(
        Output("click-output", "children"),
        Input("disabled-button", "n_clicks"),
    )
    def update_clicks(n_clicks):
        return f"Clicks: {n_clicks or 0}"

    @app.callback(
        Output("blur-output", "children"),
        Input("disabled-button", "n_blur"),
    )
    def update_blur(n_blur):
        return f"Blurs: {n_blur or 0}"

    dash_dcc.start_server(app)

    button = dash_dcc.find_element(".disabled-test-button")
    other_element = dash_dcc.find_element("#other-element")

    # Verify button is disabled
    assert button.get_attribute("disabled") is not None

    # Initial state
    dash_dcc.wait_for_text_to_equal("#click-output", "Clicks: 0")
    dash_dcc.wait_for_text_to_equal("#blur-output", "Blurs: 0")

    # Try to click - should not increment
    button.click()

    # Give it a moment and verify it's still 0
    import time

    time.sleep(0.5)

    click_text = dash_dcc.find_element("#click-output").text
    assert click_text == "Clicks: 0", "Disabled button should not trigger clicks"

    # Try to blur by clicking other element - should not increment
    other_element.click()

    time.sleep(0.5)

    blur_text = dash_dcc.find_element("#blur-output").text
    assert blur_text == "Blurs: 0", "Disabled button should not trigger blur events"

    assert dash_dcc.get_logs() == []


def test_btev003_button_states_visual(dash_dcc):
    """Visual test for button states: base, hover, and focus in one snapshot"""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.H3("Base State"),
                    dcc.Button("Base Button", id="base-button", className="state-base"),
                ],
                style={"marginBottom": "30px"},
            ),
            html.Div(
                [
                    html.H3("Hover State"),
                    dcc.Button(
                        "Hover Button", id="hover-button", className="state-hover"
                    ),
                ],
                style={"marginBottom": "30px"},
            ),
            html.Div(
                [
                    html.H3("Focus State"),
                    dcc.Button(
                        "Focus Button", id="focus-button", className="state-focus"
                    ),
                ],
                style={"marginBottom": "30px"},
            ),
        ],
        style={"padding": "40px"},
    )

    dash_dcc.start_server(app)

    # Wait for all buttons to render
    dash_dcc.wait_for_element(".state-base")

    # Set up each state
    # Tab to focus the focus button (using keyboard navigation)
    body = dash_dcc.find_element("body")
    body.send_keys(Keys.TAB)  # Focus base button
    body.send_keys(Keys.TAB)  # Focus hover button
    body.send_keys(Keys.TAB)  # Focus focus button

    # Hover over the hover button
    hover_button = dash_dcc.find_element(".state-hover")
    ActionChains(dash_dcc.driver).move_to_element(hover_button).perform()

    # Take single snapshot showing all states
    dash_dcc.percy_snapshot("Button States - Base, Hover, Focus")

    assert dash_dcc.get_logs() == []
