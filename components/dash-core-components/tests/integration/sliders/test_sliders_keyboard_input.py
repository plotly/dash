from dash import Dash, Input, Output, dcc, html
from selenium.webdriver.common.keys import Keys


def test_slkb001_input_constrained_by_min_max(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Slider(
                id="slider",
                min=1,
                max=20,
                value=5,
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
    dash_dcc.wait_for_text_to_equal("#value", "value is 5")

    inpt = dash_dcc.find_element("#slider .dash-range-slider-max-input")

    inpt.send_keys(Keys.BACKSPACE, 4, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is 4")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is 4")

    # cannot enter a value greater than `max`
    inpt.send_keys(Keys.BACKSPACE, 42, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is 20")

    # cannot enter a value less than `min`
    inpt.send_keys(Keys.ARROW_LEFT, Keys.ARROW_LEFT, "-", Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is 1")

    # cannot enter a value less than `min`
    inpt.send_keys(5, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is 15")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is 15")

    assert dash_dcc.get_logs() == []


def test_slkb002_range_input_constrained_by_min_max(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RangeSlider(
                id="slider",
                min=1,
                max=20,
                value=[5, 7],
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
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 7]")

    min_inpt = dash_dcc.find_element("#slider .dash-range-slider-min-input")
    max_inpt = dash_dcc.find_element("#slider .dash-range-slider-max-input")

    max_inpt.send_keys(Keys.BACKSPACE, 8, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 8]")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is [5, 8]")

    min_inpt.send_keys(Keys.BACKSPACE, 4, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [4, 8]")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is [4, 8]")

    # cannot enter a value greater than `max`
    max_inpt.send_keys(Keys.BACKSPACE, 42, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [4, 20]")

    # cannot enter a value less than `min`
    min_inpt.send_keys(Keys.ARROW_LEFT, Keys.ARROW_LEFT, "-", Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [1, 20]")

    # cannot enter a value less than `min`
    max_inpt.send_keys(5, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [1, 5]")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is [1, 5]")

    # cannot enter a value less than `min`
    min_inpt.send_keys(Keys.BACKSPACE, 7, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 5]")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is [7, 5]")

    assert dash_dcc.get_logs() == []


def test_slkb003_input_constrained_by_step(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Slider(
                id="slider",
                min=-20,
                max=20,
                step=5,
                value=5,
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
    dash_dcc.wait_for_text_to_equal("#value", "value is 5")

    inpt = dash_dcc.find_element("#slider .dash-range-slider-max-input")

    inpt.send_keys(Keys.BACKSPACE, -15, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is -15")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is -15")

    inpt.send_keys(Keys.BACKSPACE, 4, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is -15")

    inpt.send_keys(Keys.BACKSPACE, 2, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is -10")

    inpt.send_keys(Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, 2, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is 0")

    inpt.send_keys(20, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is 20")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is 20")

    assert dash_dcc.get_logs() == []


def test_slkb004_range_input_constrained_by_step(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RangeSlider(
                id="slider",
                min=-20,
                max=20,
                step=5,
                value=[-5, 5],
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
    dash_dcc.wait_for_text_to_equal("#value", "value is [-5, 5]")

    min_inpt = dash_dcc.find_element("#slider .dash-range-slider-min-input")
    max_inpt = dash_dcc.find_element("#slider .dash-range-slider-max-input")

    max_inpt.send_keys(Keys.BACKSPACE, 19, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [-5, 20]")

    min_inpt.send_keys(Keys.BACKSPACE, Keys.BACKSPACE, -14, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [-15, 20]")

    assert dash_dcc.get_logs() == []


def test_slkb005_input_decimals_precision(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Slider(
                id="slider",
                min=-20.5,
                max=20.5,
                step=0.01,
                value=5,
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
    dash_dcc.wait_for_text_to_equal("#value", "value is 5")

    inpt = dash_dcc.find_element("#slider .dash-range-slider-max-input")

    # value should respect the slider's `step` prop
    inpt.send_keys(Keys.BACKSPACE, 3.14159, Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is 3.14")
    dash_dcc.wait_for_text_to_equal("#drag_value", "drag_value is 3.14")

    assert dash_dcc.get_logs() == []
