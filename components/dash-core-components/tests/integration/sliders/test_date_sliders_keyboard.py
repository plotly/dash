from datetime import date
from dash import Dash, Input, Output, dcc, html
from selenium.webdriver.common.keys import Keys


def test_dslkb001_input_constrained_by_min_max_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 6, 1),
                max=date(2024, 6, 20),
                value=date(2024, 6, 5),
                display_format="YYYY-MM-DD",
                allow_direct_input=True,
            ),
            html.Div(id="value"),
            html.Div(id="drag_value"),
        ]
    )

    @app.callback(Output("value", "children"), [Input("slider", "value")])
    def update_output(value):
        return f"value is {value}"

    @app.callback(Output("drag_value", "children"), [Input("slider", "drag_value")])
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-06-05")

    input_container = dash_dcc.find_element(".dash-range-slider-min-input")
    inpt = input_container.find_element("tag name", "input")

    # Clear old value
    inpt.click()
    inpt.send_keys(Keys.END)
    for _ in range(12):
        inpt.send_keys(Keys.BACKSPACE)
    inpt.send_keys("2024-06-04", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-06-04")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is 2024-06-04")

    # Values greater than max boundaries must be rejected
    inpt.click()
    inpt.send_keys(Keys.END)
    for _ in range(12):
        inpt.send_keys(Keys.BACKSPACE)
    inpt.send_keys("2024-06-25", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-06-04")

    # Values less than min boundaries must be rejected
    inpt.click()
    inpt.send_keys(Keys.END)
    for _ in range(12):
        inpt.send_keys(Keys.BACKSPACE)
    inpt.send_keys("2024-05-15", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-06-04")

    assert dash_dcc.get_logs() == []


def test_dslkb002_range_input_constrained_by_min_max_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 6, 1),
                max=date(2024, 6, 20),
                value=[date(2024, 6, 5), date(2024, 6, 7)],
                display_format="YYYY-MM-DD",
                allow_direct_input=True,
            ),
            html.Div(id="value"),
            html.Div(id="drag_value"),
        ]
    )

    @app.callback(Output("value", "children"), [Input("slider", "value")])
    def update_output(value):
        return f"value is {value}"

    @app.callback(Output("drag_value", "children"), [Input("slider", "drag_value")])
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-06-05', '2024-06-07']")

    min_container = dash_dcc.find_element(".dash-range-slider-min-input")
    max_container = dash_dcc.find_element(".dash-range-slider-max-input")
    min_inpt = min_container.find_element("tag name", "input")
    max_inpt = max_container.find_element("tag name", "input")

    max_inpt.click()
    max_inpt.send_keys(Keys.END)
    for _ in range(12):
        max_inpt.send_keys(Keys.BACKSPACE)
    max_inpt.send_keys("2024-06-08", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-06-05', '2024-06-08']")
    dash_dcc.wait_for_text_to_equal(
        "#drag_value", "drag_value is ['2024-06-05', '2024-06-08']"
    )

    min_inpt.click()
    min_inpt.send_keys(Keys.END)
    for _ in range(12):
        min_inpt.send_keys(Keys.BACKSPACE)
    min_inpt.send_keys("2024-06-04", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-06-04', '2024-06-08']")

    # Value crossing max boundaries is rejected
    max_inpt.click()
    max_inpt.send_keys(Keys.END)
    for _ in range(12):
        max_inpt.send_keys(Keys.BACKSPACE)
    max_inpt.send_keys("2024-06-25", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-06-04', '2024-06-08']")

    # Value crossing min boundaries is rejected
    min_inpt.click()
    min_inpt.send_keys(Keys.END)
    for _ in range(12):
        min_inpt.send_keys(Keys.BACKSPACE)
    min_inpt.send_keys("2024-05-15", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-06-04', '2024-06-08']")

    assert dash_dcc.get_logs() == []


# =============================================================================
# 2. INPUT CONSTRAINED BY CALENDAR STEP INTERVALS
# =============================================================================


def test_dslkb003_input_constrained_by_step_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 6, 1),
                max=date(2024, 6, 30),
                step=5,
                step_unit="days",
                value=date(2024, 6, 1),
                display_format="YYYY-MM-DD",
                allow_direct_input=True,
            ),
            html.Div(id="value"),
            html.Div(id="drag_value"),
        ]
    )

    @app.callback(Output("value", "children"), [Input("slider", "value")])
    def update_output(value):
        return f"value is {value}"

    @app.callback(Output("drag_value", "children"), [Input("slider", "drag_value")])
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-06-01")

    input_container = dash_dcc.find_element(".dash-range-slider-min-input")
    inpt = input_container.find_element("tag name", "input")

    inpt.click()
    inpt.send_keys(Keys.END)
    for _ in range(12):
        inpt.send_keys(Keys.BACKSPACE)
    inpt.send_keys("2024-06-11", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-06-11")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is 2024-06-11")

    # Any off-step input gets rejected
    inpt.click()
    inpt.send_keys(Keys.END)
    for _ in range(12):
        inpt.send_keys(Keys.BACKSPACE)
    inpt.send_keys("2024-06-14", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-06-11")

    # Valid step alignment matches smoothly
    inpt.click()
    inpt.send_keys(Keys.END)
    for _ in range(12):
        inpt.send_keys(Keys.BACKSPACE)
    inpt.send_keys("2024-06-16", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-06-16")

    assert dash_dcc.get_logs() == []


def test_dslkb004_range_input_constrained_by_step_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 6, 1),
                max=date(2024, 6, 30),
                step=5,
                step_unit="days",
                value=[date(2024, 6, 1), date(2024, 6, 11)],
                display_format="YYYY-MM-DD",
                allow_direct_input=True,
            ),
            html.Div(id="value"),
            html.Div(id="drag_value"),
        ]
    )

    @app.callback(Output("value", "children"), [Input("slider", "value")])
    def update_output(value):
        return f"value is {value}"

    @app.callback(Output("drag_value", "children"), [Input("slider", "drag_value")])
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-06-01', '2024-06-11']")

    min_container = dash_dcc.find_element(".dash-range-slider-min-input")
    max_container = dash_dcc.find_element(".dash-range-slider-max-input")
    min_inpt = min_container.find_element("tag name", "input")
    max_inpt = max_container.find_element("tag name", "input")

    max_inpt.click()
    max_inpt.send_keys(Keys.END)
    for _ in range(12):
        max_inpt.send_keys(Keys.BACKSPACE)
    max_inpt.send_keys("2024-06-26", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-06-01', '2024-06-26']")

    min_inpt.click()
    min_inpt.send_keys(Keys.END)
    for _ in range(12):
        min_inpt.send_keys(Keys.BACKSPACE)
    min_inpt.send_keys("2024-06-06", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-06-06', '2024-06-26']")

    assert dash_dcc.get_logs() == []


def test_dslkb005_input_date_format_precision_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 6, 1),
                display_format="DD/MM/YYYY",
                allow_direct_input=True,
            ),
            html.Div(id="value"),
            html.Div(id="drag_value"),
        ]
    )

    @app.callback(Output("value", "children"), [Input("slider", "value")])
    def update_output(value):
        return f"value is {value}"

    @app.callback(Output("drag_value", "children"), [Input("slider", "drag_value")])
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-06-01")

    input_container = dash_dcc.find_element(".dash-range-slider-min-input")
    inpt = input_container.find_element("tag name", "input")

    inpt.click()
    inpt.send_keys(Keys.END)
    for _ in range(12):
        inpt.send_keys(Keys.BACKSPACE)
    inpt.send_keys("15/08/2024", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is 2024-08-15")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is 2024-08-15")

    assert dash_dcc.get_logs() == []


def test_dslkb006_input_date_format_precision_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 6, 1), date(2024, 9, 1)],
                display_format="DD/MM/YYYY",
                allow_direct_input=True,
            ),
            html.Div(id="value"),
            html.Div(id="drag_value"),
        ]
    )

    @app.callback(Output("value", "children"), [Input("slider", "value")])
    def update_output(value):
        return f"value is {value}"

    @app.callback(Output("drag_value", "children"), [Input("slider", "drag_value")])
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-06-01', '2024-09-01']")

    min_container = dash_dcc.find_element(".dash-range-slider-min-input")
    min_inpt = min_container.find_element("tag name", "input")

    min_inpt.click()
    min_inpt.send_keys(Keys.END)
    for _ in range(12):
        min_inpt.send_keys(Keys.BACKSPACE)
    min_inpt.send_keys("25/12/2024", Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#value", "value is ['2024-12-25', '2024-09-01']")

    assert dash_dcc.get_logs() == []
