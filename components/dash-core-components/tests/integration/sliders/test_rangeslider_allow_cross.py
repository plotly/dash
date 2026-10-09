from dash import Dash, Input, Output, dcc, html
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def assert_no_browser_errors(dash_dcc):
    logs = dash_dcc.get_logs()
    assert logs in ([], None)


def test_rangeslider_click_updates_callback(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "400px"},
        children=[
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
            ),
            html.Div(id="out"),
        ],
    )

    @app.callback(Output("out", "children"), Input("range-slider", "value"))
    def update_output(value):
        return f"{value[0]}-{value[1]}"

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#out", "5-15")

    slider = dash_dcc.find_element("#range-slider")
    dash_dcc.click_at_coord_fractions(slider, 0.2, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "2-15")

    dash_dcc.click_at_coord_fractions(slider, 0.51, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "2-10")

    assert len(dash_dcc.find_elements("#range-slider .dash-slider-thumb-1")) == 1
    assert len(dash_dcc.find_elements("#range-slider .dash-slider-thumb-2")) == 1
    assert_no_browser_errors(dash_dcc)


def test_rangeslider_direct_inputs_update_callbacks(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
            ),
            html.Div(id="value"),
            html.Div(id="drag-value"),
        ]
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    max_input = dash_dcc.find_element("#range-slider .dash-range-slider-max-input")
    assert min_input.get_attribute("value") == "5"
    assert max_input.get_attribute("value") == "15"

    dash_dcc.clear_input(min_input)
    min_input.send_keys("4", Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [4, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [4, 15]")

    dash_dcc.clear_input(max_input)
    max_input.send_keys("18", Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [4, 18]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [4, 18]")

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_min_direct_input_above_max_clamps_to_max_handle(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
                allowCross=False,
                updatemode="drag",
            ),
            html.Div(id="value"),
            html.Div(id="drag-value"),
        ]
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    dash_dcc.clear_input(min_input)
    min_input.send_keys("18")

    dash_dcc.wait_for_text_to_equal("#value", "value is [15, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [15, 15]")
    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    max_input = dash_dcc.find_element("#range-slider .dash-range-slider-max-input")
    assert min_input.get_attribute("value") == "18"
    assert max_input.get_attribute("value") == "15"

    min_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-1")
    max_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-2")
    min_thumb_center = dash_dcc.driver.execute_script(
        "const rect = arguments[0].getBoundingClientRect();"
        "return rect.left + rect.width / 2;",
        min_thumb,
    )
    max_thumb_center = dash_dcc.driver.execute_script(
        "const rect = arguments[0].getBoundingClientRect();"
        "return rect.left + rect.width / 2;",
        max_thumb,
    )
    assert abs(min_thumb_center - max_thumb_center) <= 1

    min_input.send_keys(Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [15, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [15, 15]")
    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    max_input = dash_dcc.find_element("#range-slider .dash-range-slider-max-input")
    assert min_input.get_attribute("value") == "15"
    assert max_input.get_attribute("value") == "15"

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_allow_cross_true_min_direct_input_above_max_allows_crossing(
    dash_dcc,
):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
                allowCross=True,
                updatemode="mouseup",
            ),
            html.Div(id="value"),
            html.Div(id="drag-value"),
        ]
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    dash_dcc.clear_input(min_input)
    min_input.send_keys("18")

    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [15, 18]")
    assert dash_dcc.find_element("#value").text == "value is [5, 15]"
    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    max_input = dash_dcc.find_element("#range-slider .dash-range-slider-max-input")
    assert min_input.get_attribute("value") == "18"
    assert max_input.get_attribute("value") == "15"
    min_input.send_keys(Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [15, 18]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [15, 18]")
    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    max_input = dash_dcc.find_element("#range-slider .dash-range-slider-max-input")
    assert min_input.get_attribute("value") == "15"
    assert max_input.get_attribute("value") == "18"

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_allow_cross_false_prevents_handle_crossing(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "400px"},
        children=[
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
                allowCross=False,
                updatemode="mouseup",
            ),
            html.Div(id="value"),
            html.Div(id="drag-value"),
            html.Div(id="state"),
        ],
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    @app.callback(
        Output("state", "children"),
        Input("range-slider", "value"),
        Input("range-slider", "drag_value"),
    )
    def update_state(value, drag_value):
        return f"value is {value}; drag_value is {drag_value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#state", "value is [5, 15]; drag_value is [5, 15]")

    slider_root = dash_dcc.find_element("#range-slider .dash-slider-root")
    min_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-1")
    dash_dcc.click_and_hold_at_coord_fractions(min_thumb, 0.5, 0.5)
    dash_dcc.move_to_coord_fractions(slider_root, 0.6, 0.5)
    dash_dcc.wait_for_text_to_equal(
        "#state", "value is [5, 15]; drag_value is [12, 15]"
    )
    active_thumb = dash_dcc.driver.switch_to.active_element
    assert "dash-slider-thumb-1" in active_thumb.get_attribute("class")
    ActionChains(dash_dcc.driver).key_down(Keys.ARROW_RIGHT).key_up(
        Keys.ARROW_RIGHT
    ).move_to_element_with_offset(
        slider_root,
        slider_root.size["width"] * 0.9,
        slider_root.size["height"] * 0.5,
    ).release().perform()
    dash_dcc.wait_for_text_to_equal(
        "#state", "value is [15, 15]; drag_value is [15, 15]"
    )

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_allow_cross_false_keyboard_clamps_active_min_thumb(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "400px"},
        children=[
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
                allowCross=False,
                updatemode="drag",
            ),
            html.Div(id="value"),
            html.Div(id="drag-value"),
        ],
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    min_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-1")
    min_thumb.click()
    for _ in range(15):
        min_thumb.send_keys(Keys.ARROW_RIGHT)

    dash_dcc.wait_for_text_to_equal("#value", "value is [15, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [15, 15]")
    min_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-1")
    max_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-2")
    assert min_thumb.get_attribute("aria-valuenow") == "15"
    assert max_thumb.get_attribute("aria-valuenow") == "15"

    min_thumb_center = dash_dcc.driver.execute_script(
        "const rect = arguments[0].getBoundingClientRect();"
        "return rect.left + rect.width / 2;",
        min_thumb,
    )
    max_thumb_center = dash_dcc.driver.execute_script(
        "const rect = arguments[0].getBoundingClientRect();"
        "return rect.left + rect.width / 2;",
        max_thumb,
    )
    assert abs(min_thumb_center - max_thumb_center) <= 1

    min_thumb.send_keys(Keys.TAB)
    active_thumb = dash_dcc.driver.switch_to.active_element
    assert "dash-slider-thumb-2" in active_thumb.get_attribute("class")
    active_thumb.send_keys(Keys.ARROW_RIGHT)
    dash_dcc.wait_for_text_to_equal("#value", "value is [15, 16]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [15, 16]")

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_home_end_update_the_focused_thumb(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "400px"},
        children=[
            dcc.RangeSlider(
                id="no-cross-slider",
                min=0,
                max=20,
                step=1,
                value=[0, 15],
                allowCross=False,
            ),
            html.Div(id="no-cross-value"),
            html.Div(id="no-cross-drag-value"),
            dcc.RangeSlider(
                id="cross-slider",
                min=0,
                max=10,
                step=3,
                value=[3, 6],
                allowCross=True,
                updatemode="drag",
            ),
            html.Div(id="cross-value"),
            html.Div(id="cross-drag-value"),
        ],
    )

    @app.callback(
        Output("no-cross-value", "children"), Input("no-cross-slider", "value")
    )
    def update_no_cross_value(value):
        return f"value is {value}"

    @app.callback(
        Output("no-cross-drag-value", "children"),
        Input("no-cross-slider", "drag_value"),
    )
    def update_no_cross_drag_value(value):
        return f"drag_value is {value}"

    @app.callback(Output("cross-value", "children"), Input("cross-slider", "value"))
    def update_cross_value(value):
        return f"value is {value}"

    @app.callback(
        Output("cross-drag-value", "children"), Input("cross-slider", "drag_value")
    )
    def update_cross_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#no-cross-value", "value is [0, 15]")
    dash_dcc.wait_for_text_to_equal("#no-cross-drag-value", "drag_value is [0, 15]")
    dash_dcc.wait_for_text_to_equal("#cross-value", "value is [3, 6]")
    dash_dcc.wait_for_text_to_equal("#cross-drag-value", "drag_value is [3, 6]")

    no_cross_max = dash_dcc.find_element("#no-cross-slider .dash-slider-thumb-2")
    no_cross_max.click()
    no_cross_max.send_keys(Keys.HOME)
    dash_dcc.wait_for_text_to_equal("#no-cross-value", "value is [0, 0]")
    dash_dcc.wait_for_text_to_equal("#no-cross-drag-value", "drag_value is [0, 0]")

    cross_max = dash_dcc.find_element("#cross-slider .dash-slider-thumb-2")
    cross_max.click()
    cross_max.send_keys(Keys.HOME)
    dash_dcc.wait_for_text_to_equal("#cross-value", "value is [0, 3]")
    dash_dcc.wait_for_text_to_equal("#cross-drag-value", "drag_value is [0, 3]")
    active_thumb = dash_dcc.driver.switch_to.active_element
    assert "dash-slider-thumb-1" in active_thumb.get_attribute("class")
    active_thumb.send_keys(Keys.ARROW_RIGHT)
    dash_dcc.wait_for_text_to_equal("#cross-value", "value is [3, 3]")
    dash_dcc.wait_for_text_to_equal("#cross-drag-value", "drag_value is [3, 3]")
    active_thumb.send_keys(Keys.END)
    dash_dcc.wait_for_text_to_equal("#cross-value", "value is [3, 9]")
    dash_dcc.wait_for_text_to_equal("#cross-drag-value", "drag_value is [3, 9]")
    active_thumb = dash_dcc.driver.switch_to.active_element
    assert "dash-slider-thumb-2" in active_thumb.get_attribute("class")

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_disabled_home_end_do_not_update_retained_focus(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Toggle disabled", id="toggle-disabled"),
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
                updatemode="drag",
            ),
            html.Div(id="disabled-state"),
            html.Div(id="value-event"),
            html.Div(id="drag-value"),
        ]
    )
    value_events = []

    @app.callback(
        Output("range-slider", "disabled"),
        Output("disabled-state", "children"),
        Input("toggle-disabled", "n_clicks"),
    )
    def toggle_disabled(n_clicks):
        disabled = bool((n_clicks or 0) % 2)
        return disabled, f"disabled is {disabled}"

    @app.callback(Output("value-event", "children"), Input("range-slider", "value"))
    def update_value(value):
        value_events.append(value)
        return f"event {len(value_events)}: {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#disabled-state", "disabled is False")
    dash_dcc.wait_for_text_to_equal("#value-event", "event 1: [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    max_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-2")
    max_thumb.click()
    assert dash_dcc.driver.switch_to.active_element == max_thumb

    dash_dcc.driver.execute_script(
        "window.dash_clientside.set_props('toggle-disabled', {n_clicks: 1});"
    )
    dash_dcc.wait_for_text_to_equal("#disabled-state", "disabled is True")
    dash_dcc.find_element("#range-slider .dash-slider-root[data-disabled]")
    max_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-2")
    dash_dcc.driver.execute_script(
        """
        const thumb = arguments[0];
        for (const key of ['Home', 'End']) {
            const options = {key, code: key, bubbles: true, cancelable: true};
            thumb.dispatchEvent(new KeyboardEvent('keydown', options));
            thumb.dispatchEvent(new KeyboardEvent('keyup', options));
        }
        """,
        max_thumb,
    )

    dash_dcc.driver.execute_script(
        "window.dash_clientside.set_props('toggle-disabled', {n_clicks: 2});"
    )
    dash_dcc.wait_for_text_to_equal("#disabled-state", "disabled is False")
    max_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-2")
    max_thumb.click()
    max_thumb.send_keys(Keys.ARROW_RIGHT)
    dash_dcc.wait_for_text_to_equal("#value-event", "event 2: [5, 16]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 16]")

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_allow_cross_tracks_thumb_through_duplicate_values(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "400px"},
        children=[
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=30,
                step=1,
                value=[0, 10, 20],
                allowCross=True,
                updatemode="drag",
            ),
            html.Div(id="value"),
            dcc.RangeSlider(
                id="descending-slider",
                min=0,
                max=30,
                step=1,
                value=[0, 10, 20],
                allowCross=True,
                updatemode="drag",
            ),
            html.Div(id="descending-value"),
        ],
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(
        Output("descending-value", "children"),
        Input("descending-slider", "value"),
    )
    def update_descending_value(value):
        return f"value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [0, 10, 20]")
    dash_dcc.wait_for_text_to_equal("#descending-value", "value is [0, 10, 20]")

    slider_root = dash_dcc.find_element("#range-slider .dash-slider-root")
    first_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-1")
    dash_dcc.click_and_hold_at_coord_fractions(first_thumb, 0.5, 0.5)
    dash_dcc.move_to_coord_fractions(slider_root, 2 / 3, 0.5)
    dash_dcc.wait_for_text_to_equal("#value", "value is [10, 20, 20]")
    dash_dcc.move_to_coord_fractions(slider_root, 0.7, 0.5)
    dash_dcc.wait_for_text_to_equal("#value", "value is [10, 20, 21]")
    dash_dcc.release()

    descending_root = dash_dcc.find_element("#descending-slider .dash-slider-root")
    third_thumb = dash_dcc.find_element("#descending-slider .dash-slider-thumb-3")
    dash_dcc.click_and_hold_at_coord_fractions(third_thumb, 0.5, 0.5)
    dash_dcc.move_to_coord_fractions(descending_root, 1 / 3, 0.5)
    dash_dcc.wait_for_text_to_equal("#descending-value", "value is [0, 10, 10]")
    active_thumb = dash_dcc.driver.switch_to.active_element
    assert "dash-slider-thumb-3" in active_thumb.get_attribute("class")
    dash_dcc.move_to_coord_fractions(descending_root, 0.3, 0.5)
    dash_dcc.wait_for_text_to_equal("#descending-value", "value is [0, 9, 10]")
    active_thumb = dash_dcc.driver.switch_to.active_element
    assert "dash-slider-thumb-2" in active_thumb.get_attribute("class")
    dash_dcc.release()

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_track_noop_start_keeps_the_closest_thumb(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "400px"},
        children=[
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=2,
                step=0.5,
                value=[0, 1, 2],
                allowCross=False,
                updatemode="drag",
            ),
            html.Div(id="value"),
            dcc.RangeSlider(
                id="duplicate-slider",
                min=0,
                max=2,
                step=0.25,
                value=[0, 1, 1, 2],
                allowCross=False,
                updatemode="drag",
            ),
            html.Div(id="duplicate-value"),
            dcc.RangeSlider(
                id="duplicate-right-slider",
                min=0,
                max=2,
                step=0.25,
                value=[0, 1, 1, 2],
                allowCross=False,
                updatemode="drag",
            ),
            html.Div(id="duplicate-right-value"),
        ],
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(
        Output("duplicate-value", "children"), Input("duplicate-slider", "value")
    )
    def update_duplicate_value(value):
        return f"value is {value}"

    @app.callback(
        Output("duplicate-right-value", "children"),
        Input("duplicate-right-slider", "value"),
    )
    def update_duplicate_right_value(value):
        return f"value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [0, 1, 2]")
    dash_dcc.wait_for_text_to_equal("#duplicate-value", "value is [0, 1, 1, 2]")
    dash_dcc.wait_for_text_to_equal("#duplicate-right-value", "value is [0, 1, 1, 2]")

    slider_root = dash_dcc.find_element("#range-slider .dash-slider-root")
    dash_dcc.click_and_hold_at_coord_fractions(slider_root, 0.1, 0.5)
    dash_dcc.move_to_coord_fractions(slider_root, 0.75, 0.5)
    dash_dcc.wait_for_text_to_equal("#value", "value is [1, 1, 2]")
    dash_dcc.release()

    duplicate_root = dash_dcc.find_element("#duplicate-slider .dash-slider-root")
    dash_dcc.click_and_hold_at_coord_fractions(duplicate_root, 0.46, 0.5)
    dash_dcc.move_to_coord_fractions(duplicate_root, 0.375, 0.5)
    dash_dcc.wait_for_text_to_equal("#duplicate-value", "value is [0, 0.75, 1, 2]")
    dash_dcc.release()

    duplicate_right_root = dash_dcc.find_element(
        "#duplicate-right-slider .dash-slider-root"
    )
    dash_dcc.click_and_hold_at_coord_fractions(duplicate_right_root, 0.54, 0.5)
    dash_dcc.move_to_coord_fractions(duplicate_right_root, 0.625, 0.5)
    dash_dcc.release()
    assert (
        dash_dcc.find_element("#duplicate-right-value").text == "value is [0, 1, 1, 2]"
    )
    duplicate_right_thumbs = dash_dcc.find_elements(
        "#duplicate-right-slider .dash-slider-thumb"
    )
    assert [
        thumb.get_attribute("aria-valuenow") for thumb in duplicate_right_thumbs
    ] == [
        "0",
        "1",
        "1",
        "2",
    ]

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_allow_cross_true_allows_handle_crossing(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "400px"},
        children=[
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
                allowCross=True,
                updatemode="drag",
            ),
            html.Div(id="value"),
            html.Div(id="drag-value"),
        ],
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    slider_root = dash_dcc.find_element("#range-slider .dash-slider-root")
    min_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-1")
    dash_dcc.click_and_hold_at_coord_fractions(min_thumb, 0.5, 0.5)
    dash_dcc.move_to_coord_fractions(slider_root, 0.9, 0.5)
    dash_dcc.wait_for_text_to_equal("#value", "value is [15, 18]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [15, 18]")
    dash_dcc.release()
    dash_dcc.wait_for_text_to_equal("#value", "value is [15, 18]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [15, 18]")

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_allow_cross_defaults_to_true(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "400px"},
        children=[
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
                updatemode="drag",
            ),
            html.Div(id="value"),
            html.Div(id="drag-value"),
        ],
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    slider_root = dash_dcc.find_element("#range-slider .dash-slider-root")
    min_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-1")
    dash_dcc.click_and_hold_at_coord_fractions(min_thumb, 0.5, 0.5)
    dash_dcc.move_to_coord_fractions(slider_root, 0.9, 0.5)
    dash_dcc.wait_for_text_to_equal("#value", "value is [15, 18]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [15, 18]")
    dash_dcc.release()

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_external_value_clears_direct_input_draft(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Set value", id="set-value"),
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
            ),
            html.Div(id="value"),
            html.Div(id="drag-value"),
            html.Div(id="set-result"),
        ]
    )

    @app.callback(
        Output("range-slider", "value"),
        Output("set-result", "children"),
        Input("set-value", "n_clicks"),
        prevent_initial_call=True,
    )
    def set_value(n_clicks):
        value = [5, 15] if n_clicks == 1 else [2, 12]
        return value, f"set {n_clicks}"

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    dash_dcc.clear_input(min_input)
    min_input.send_keys("999")
    assert min_input.get_attribute("value") == "999"
    assert dash_dcc.driver.switch_to.active_element == min_input

    dash_dcc.driver.execute_script(
        "window.dash_clientside.set_props('set-value', {n_clicks: 1});"
    )
    dash_dcc.wait_for_text_to_equal("#set-result", "set 1")

    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    max_input = dash_dcc.find_element("#range-slider .dash-range-slider-max-input")
    assert min_input.get_attribute("value") == "5"
    assert max_input.get_attribute("value") == "15"
    assert dash_dcc.driver.switch_to.active_element == min_input

    dash_dcc.clear_input(min_input)
    min_input.send_keys("9")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [9, 15]")
    assert dash_dcc.find_element("#value").text == "value is [5, 15]"
    assert dash_dcc.driver.switch_to.active_element == min_input

    dash_dcc.driver.execute_script(
        "window.dash_clientside.set_props('set-value', {n_clicks: 2});"
    )
    dash_dcc.wait_for_text_to_equal("#set-result", "set 2")
    dash_dcc.wait_for_text_to_equal("#value", "value is [2, 12]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [2, 12]")

    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    max_input = dash_dcc.find_element("#range-slider .dash-range-slider-max-input")
    assert min_input.get_attribute("value") == "2"
    assert max_input.get_attribute("value") == "12"
    assert dash_dcc.driver.switch_to.active_element == min_input
    min_input.send_keys(Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [2, 12]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [2, 12]")

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_external_handle_shrink_resets_keyboard_transaction(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[0, 10, 20],
                updatemode="mouseup",
            ),
            html.Div(id="value-event"),
            html.Div(id="drag-value"),
        ]
    )
    value_events = []

    @app.callback(Output("value-event", "children"), Input("range-slider", "value"))
    def update_value(value):
        value_events.append(value)
        return f"event {len(value_events)}: {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value-event", "event 1: [0, 10, 20]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [0, 10, 20]")

    third_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-3")
    third_thumb.click()
    ActionChains(dash_dcc.driver).key_down(Keys.ARROW_LEFT).perform()
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [0, 10, 19]")
    assert dash_dcc.find_element("#value-event").text == "event 1: [0, 10, 20]"

    dash_dcc.driver.execute_script(
        "window.dash_clientside.set_props('range-slider', {value: [0, 10]});"
    )
    dash_dcc.wait_for_text_to_equal("#value-event", "event 2: [0, 10]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [0, 10]")
    assert len(dash_dcc.find_elements("#range-slider .dash-slider-thumb")) == 2

    ActionChains(dash_dcc.driver).key_up(Keys.ARROW_LEFT).perform()
    first_thumb = dash_dcc.find_element("#range-slider .dash-slider-thumb-1")
    first_thumb.send_keys(Keys.ARROW_RIGHT)
    dash_dcc.wait_for_text_to_equal("#value-event", "event 3: [1, 10]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [1, 10]")

    assert_no_browser_errors(dash_dcc)


def test_rangeslider_mouseup_input_blur_resynchronizes_drag_value(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RangeSlider(
                id="range-slider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
                allowCross=False,
                updatemode="mouseup",
            ),
            html.Div(id="value"),
            html.Div(id="drag-value"),
        ]
    )

    @app.callback(Output("value", "children"), Input("range-slider", "value"))
    def update_value(value):
        return f"value is {value}"

    @app.callback(Output("drag-value", "children"), Input("range-slider", "drag_value"))
    def update_drag_value(value):
        return f"drag_value is {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    min_input = dash_dcc.find_element("#range-slider .dash-range-slider-min-input")
    dash_dcc.clear_input(min_input)
    min_input.send_keys("6")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [6, 15]")
    assert dash_dcc.find_element("#value").text == "value is [5, 15]"

    dash_dcc.clear_input(min_input)
    min_input.send_keys("5.4", Keys.TAB)
    dash_dcc.wait_for_text_to_equal("#value", "value is [5, 15]")
    dash_dcc.wait_for_text_to_equal("#drag-value", "drag_value is [5, 15]")

    assert_no_browser_errors(dash_dcc)
