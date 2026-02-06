import time
import sys
import pytest
from dash import Dash, Input, Output, html, dcc
from selenium.webdriver.common.keys import Keys


def test_inni001_invalid_numbers(ninput_app, dash_dcc):
    dash_dcc.start_server(ninput_app)
    for invalid_number in ("10e10000", "e+++eeeeeE-", "12-.3"):
        for debounce in ("false", "true"):
            elem = dash_dcc.find_element(f"#input_{debounce}")
            assert not elem.get_attribute("value"), "input should have no initial value"

            # onblur
            elem.send_keys(invalid_number)
            elem.send_keys(Keys.TAB)

            dash_dcc.wait_for_text_to_equal(f"#div_{debounce}", "")

            # Enter keypress
            dash_dcc.clear_input(elem)
            elem.send_keys(invalid_number)
            elem.send_keys(Keys.ENTER)

            dash_dcc.wait_for_text_to_equal(f"#div_{debounce}", "")

            dash_dcc.clear_input(elem)

    assert dash_dcc.get_logs() == []


def test_inni002_invalid_numbers_ui(dash_dcc, ninput_app):
    dash_dcc.start_server(ninput_app)
    elem = dash_dcc.find_element("#input_false")

    elem.send_keys("5e-325")  # smaller than Number.MIN_VALUE
    assert dash_dcc.wait_for_text_to_equal("#div_false", "0")

    dash_dcc.clear_input(elem)
    elem.send_keys("0.0.0")
    elem.send_keys(Keys.TAB)

    assert dash_dcc.find_element("#div_false").text != "0.0"
    time.sleep(0.5)
    dash_dcc.percy_snapshot("inni002 - input invalid number")

    assert dash_dcc.get_logs() == []


def test_inni003_invalid_numbers_range(dash_dcc, input_range_app):
    dash_dcc.start_server(input_range_app)  # range [10, 10000] step=3

    elem_range = dash_dcc.find_element("#range")
    elem_range.send_keys("1999")
    assert dash_dcc.find_element("#out").text == "1999"

    for invalid_number in ("0.0", "12", "10e10"):
        elem_range.send_keys(invalid_number)
        dash_dcc.wait_for_text_to_equal("#out", ""), "invalid value should return none"
        dash_dcc.clear_input(elem_range)

    elem_range.send_keys("-13")
    dash_dcc.wait_for_text_to_equal("#out", ""), "invalid value should return none"

    time.sleep(0.5)
    dash_dcc.percy_snapshot("inni003 - number out of range")

    assert dash_dcc.get_logs() == []


def test_inni004_steppers(dash_dcc, debounce_number_app):
    dash_dcc.start_server(debounce_number_app)

    # Test input with min=10, max=10000, step=3 (#input-fast)
    input_elem = dash_dcc.find_element("#input-fast")
    increment_btn = dash_dcc.find_element("#input-fast~.dash-stepper-increment")
    decrement_btn = dash_dcc.find_element("#input-fast~.dash-stepper-decrement")

    # Verify steppers exist
    assert increment_btn.is_displayed(), "Increment stepper should be visible"
    assert decrement_btn.is_displayed(), "Decrement stepper should be visible"

    # Set initial value to 100
    input_elem.send_keys("100")
    dash_dcc.wait_for_text_to_equal("#div-fast", "100")

    # Test increment stepper - should increase by step=3
    increment_btn.click()
    dash_dcc.wait_for_text_to_equal("#div-fast", "103")

    # Test decrement stepper - should decrease by step=3
    decrement_btn.click()
    dash_dcc.wait_for_text_to_equal("#div-fast", "100")

    # Test multiple increments
    increment_btn.click()
    increment_btn.click()
    dash_dcc.wait_for_text_to_equal("#div-fast", "106")

    # Test that steppers respect min constraint
    dash_dcc.clear_input(input_elem)
    input_elem.send_keys("11")  # Close to min=10
    decrement_btn.click()  # Should go to 10 (min)
    dash_dcc.wait_for_text_to_equal("#div-fast", "10")

    # Verify decrement button is disabled at minimum
    assert (
        decrement_btn.get_attribute("disabled") == "true"
    ), "Decrement should be disabled at minimum"

    # Test that steppers respect max constraint
    dash_dcc.clear_input(input_elem)
    input_elem.send_keys("9999")  # Close to max=10000
    increment_btn.click()  # Should go to 10000 (max)
    dash_dcc.wait_for_text_to_equal("#div-fast", "10000")

    # Verify increment button is disabled at maximum
    assert (
        increment_btn.get_attribute("disabled") == "true"
    ), "Increment should be disabled at maximum"

    assert dash_dcc.get_logs() == []


def test_inni005_stepper_decrement_bug(dash_dcc, input_range_app):
    """Test that decrement button works correctly with min/max constraints on initial render."""

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="number", value=17, type="number", min=10, max=23),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), [Input("number", "value")])
    def update_output(val):
        return val

    dash_dcc.start_server(app)

    decrement_btn = dash_dcc.find_element(".dash-stepper-decrement")

    # Initial value is 17, should be able to decrement to 16
    decrement_btn.click()
    dash_dcc.wait_for_text_to_equal("#output", "16")

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("step", [0.1, 0.01, 0.001, 0.0001])
def test_inni006_stepper_floating_point_precision(dash_dcc, step):
    """Test that stepper increments/decrements with decimal steps don't accumulate floating point errors."""

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="decimal-input", value=0, type="number", step=step),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), [Input("decimal-input", "value")])
    def update_output(val):
        return val

    dash_dcc.start_server(app)
    increment_btn = dash_dcc.find_element(".dash-stepper-increment")
    decrement_btn = dash_dcc.find_element(".dash-stepper-decrement")

    # Determine decimal places for formatting
    decimal_places = len(str(step).split(".")[1]) if "." in str(step) else 0
    num_clicks = 9

    # Test increment: without precision fix, accumulates floating point errors (e.g., 0.30000000000000004)
    for i in range(1, num_clicks + 1):
        increment_btn.click()
        expected = format(step * i, f".{decimal_places}f")
        dash_dcc.wait_for_text_to_equal("#output", expected)

    # Test decrement: should go back down through the same values
    for i in range(num_clicks - 1, 0, -1):
        decrement_btn.click()
        expected = format(step * i, f".{decimal_places}f")
        dash_dcc.wait_for_text_to_equal("#output", expected)

    # One more decrement to get back to 0
    decrement_btn.click()
    dash_dcc.wait_for_text_to_equal("#output", "0")

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("step", [0.00001, 0.000001])
def test_inni007_stepper_very_small_steps(dash_dcc, step):
    """Test that stepper works correctly with very small decimal steps."""

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="decimal-input", value=0, type="number", step=step),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), [Input("decimal-input", "value")])
    def update_output(val):
        return val

    dash_dcc.start_server(app)
    increment_btn = dash_dcc.find_element(".dash-stepper-increment")
    decrement_btn = dash_dcc.find_element(".dash-stepper-decrement")

    # For very small steps, format with enough precision then strip trailing zeros
    step_str = f"{step:.10f}".rstrip("0").rstrip(".")
    decimal_places = len(step_str.split(".")[1]) if "." in step_str else 0
    num_clicks = 5

    # Test increment
    for i in range(1, num_clicks + 1):
        increment_btn.click()
        expected = f"{step * i:.{decimal_places}f}".rstrip("0").rstrip(".")
        dash_dcc.wait_for_text_to_equal("#output", expected)

    # Test decrement
    for i in range(num_clicks - 1, 0, -1):
        decrement_btn.click()
        expected = f"{step * i:.{decimal_places}f}".rstrip("0").rstrip(".")
        dash_dcc.wait_for_text_to_equal("#output", expected)

    # One more decrement to get back to 0
    decrement_btn.click()
    dash_dcc.wait_for_text_to_equal("#output", "0")

    assert dash_dcc.get_logs() == []


def test_inni010_valid_numbers(dash_dcc, ninput_app):
    dash_dcc.start_server(ninput_app)
    for num, op in (
        ("1.0", lambda x: int(float(x))),  # limitation of js/json
        ("10e10", lambda x: int(float(x))),
        ("-1.0001", float),
        (str(sys.float_info.max), float),
        (str(sys.float_info.min), float),
    ):
        elem = dash_dcc.find_element("#input_false")
        elem.send_keys(num)
        assert dash_dcc.wait_for_text_to_equal(
            "#div_false", str(op(num))
        ), "the valid number should be converted to expected form in callback"
        dash_dcc.clear_input(elem)

    assert dash_dcc.get_logs() == []
