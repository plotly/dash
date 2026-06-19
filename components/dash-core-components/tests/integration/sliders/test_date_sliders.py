import time
from datetime import date
from multiprocessing import Lock

from dash import Dash, Input, Output, dcc, html


def test_dslsl001_basic_render_and_callback_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 6, 15),
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"Selected: {value}"

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#out", "Selected: 2024-06-15")
    assert dash_dcc.get_logs() == []


def test_dslsl002_basic_render_and_callback_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 3, 1), date(2024, 9, 1)],
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"{value[0]} to {value[1]}"

    dash_dcc.start_server(app)
    expected_text = f"{date(2024, 3, 1)} to {date(2024, 9, 1)}"
    dash_dcc.wait_for_text_to_equal("#out", expected_text)
    assert dash_dcc.get_logs() == []


# CLICK SELECTION
def test_dslsl003_click_moves_handle_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 1, 1),
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"Selected: {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(1000, 600)
    dash_dcc.wait_for_text_to_equal("#out", "Selected: 2024-01-01")

    dash_dcc.wait_for_element(".dash-date-range-slider-wrapper")
    slider_wrapper = dash_dcc.find_element(".dash-date-range-slider-wrapper")

    dash_dcc.click_at_coord_fractions(slider_wrapper, 0.5, 0.5)

    dash_dcc.wait_for_text_to_equal(
        "#out",
        "Selected: 2024-07-02",
    )
    assert dash_dcc.get_logs() == []


def test_dslsl004_click_moves_handle_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 1, 1), date(2024, 12, 31)],
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"{value[0]} to {value[1]}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(1000, 600)

    dash_dcc.wait_for_text_to_equal(
        "#out", f"{date(2024, 1, 1)} to {date(2024, 12, 31)}"
    )

    dash_dcc.wait_for_element(".dash-slider-root")
    slider = dash_dcc.find_element(".dash-slider-root")

    dash_dcc.click_at_coord_fractions(slider, 0.25, 0.5)

    dash_dcc.wait_for_element("#out")
    dash_dcc.wait_for_text_to_equal(
        "#out",
        "2024-04-01 to 2024-12-31",
    )
    assert dash_dcc.get_logs() == []


# DRAG VALUE
def test_dslsl005_drag_value_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 1, 1),
                tooltip={"always_visible": True},
            ),
            html.Div(id="out-value"),
            html.Div(id="out-drag"),
        ]
    )

    @app.callback(Output("out-value", "children"), Input("slider", "value"))
    def cb_value(value):
        return f"Value: {value}"

    @app.callback(Output("out-drag", "children"), Input("slider", "drag_value"))
    def cb_drag(value):
        if not value:
            return "no drag"
        return f"Drag: {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(1000, 600)
    dash_dcc.wait_for_text_to_equal("#out-value", "Value: 2024-01-01")
    dash_dcc.wait_for_text_to_equal("#out-drag", "Drag: 2024-01-01")

    slider = dash_dcc.find_element(".dash-slider-root")

    dash_dcc.click_and_hold_at_coord_fractions(slider, 0.02, 0.5)
    dash_dcc.move_to_coord_fractions(slider, 0.50, 0.5)

    dash_dcc.wait_for_text_to_equal("#out-drag", "Drag: 2024-07-02")

    dash_dcc.wait_for_text_to_equal("#out-value", "Value: 2024-01-01")

    dash_dcc.release()

    dash_dcc.wait_for_text_to_equal("#out-value", "Value: 2024-07-02")
    assert dash_dcc.get_logs() == []


def test_dslsl006_drag_value_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 1, 1), date(2024, 6, 30)],
                tooltip={"always_visible": True},
            ),
            html.Div(id="out-value"),
            html.Div(id="out-drag"),
        ]
    )

    @app.callback(Output("out-value", "children"), Input("slider", "value"))
    def cb_value(value):
        return f"{value[0]} to {value[1]}"

    @app.callback(Output("out-drag", "children"), Input("slider", "drag_value"))
    def cb_drag(value):
        if not value:
            return "no drag"
        return f"drag: {value[0]} to {value[1]}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(1000, 600)
    dash_dcc.wait_for_text_to_equal(
        "#out-value",
        f"{date(2024, 1, 1)} to {date(2024, 6, 30)}",
    )

    dash_dcc.wait_for_text_to_equal(
        "#out-drag",
        f"drag: {date(2024, 1, 1)} to {date(2024, 6, 30)}",
    )

    slider = dash_dcc.find_element(".dash-slider-root")

    dash_dcc.click_and_hold_at_coord_fractions(slider, 0.1, 0.5)
    dash_dcc.move_to_coord_fractions(slider, 0.5, 0.5)

    assert dash_dcc.find_element("#out-drag").text != (
        f"drag: {date(2024, 1, 1)} to {date(2024, 6, 30)}"
    )

    dash_dcc.wait_for_text_to_equal(
        "#out-value",
        f"{date(2024, 1, 1)} to {date(2024, 6, 30)}",
    )

    dash_dcc.release()

    assert dash_dcc.find_element("#out-value").text != (
        f"{date(2024, 1, 1)} to {date(2024, 6, 30)}"
    )

    assert dash_dcc.get_logs() == []


# TOOLTIP
def test_dslsl007_tooltip_shows_formatted_date_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 6, 1),
                tooltip={"always_visible": True, "placement": "top"},
                display_format="YYYY-MM-DD",
            ),
        ],
        style={"padding": "60px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-tooltip")

    tooltips = dash_dcc.find_elements(".dash-slider-tooltip")
    assert len(tooltips) == 1

    tooltip_texts = [tooltip.text for tooltip in tooltips]
    assert "2024-06-01" in tooltip_texts

    assert dash_dcc.get_logs() == []


def test_dslsl008_tooltip_shows_formatted_date_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 6, 1), date(2024, 9, 1)],
                tooltip={"always_visible": True, "placement": "top"},
                display_format="YYYY-MM-DD",
            ),
        ],
        style={"padding": "60px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-tooltip")

    tooltips = dash_dcc.find_elements(".dash-slider-tooltip")
    assert len(tooltips) == 2

    tooltip_texts = [tooltip.text for tooltip in tooltips]
    assert "2024-06-01" in tooltip_texts
    assert "2024-09-01" in tooltip_texts

    assert dash_dcc.get_logs() == []


# DISPLAY FORMAT
def test_dslsl009_display_format_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 6, 1),
                display_format="DD/MM/YYYY",
                tooltip={"always_visible": True},
            ),
        ],
        style={"padding": "60px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-tooltip")

    tooltips = dash_dcc.find_elements(".dash-slider-tooltip")
    assert len(tooltips) == 1
    assert tooltips[0].text == "01/06/2024"

    assert dash_dcc.get_logs() == []


def test_dslsl010_display_format_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 6, 1), date(2024, 9, 1)],
                display_format="DD/MM/YYYY",
                tooltip={"always_visible": True},
            ),
        ],
        style={"padding": "60px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-tooltip")

    tooltips = dash_dcc.find_elements(".dash-slider-tooltip")
    assert len(tooltips) == 2

    tooltip_texts = [t.text for t in tooltips]
    assert sorted(tooltip_texts) == [
        "01/06/2024",
        "01/09/2024",
    ]

    assert dash_dcc.get_logs() == []


# STEP DAYS
def test_dslsl011_step_days_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 1, 31),
                value=date(2024, 1, 1),
                step=7,
                step_unit="days",
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"{value}"

    dash_dcc.start_server(app)
    slider = dash_dcc.find_element(".dash-slider-root")
    dash_dcc.click_at_coord_fractions(slider, 0.48, 0.5)

    dash_dcc.wait_for_text_to_equal("#out", "2024-01-15")
    assert dash_dcc.get_logs() == []


def test_dslsl012_step_days_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 1, 29),
                value=[date(2024, 1, 1), date(2024, 1, 29)],
                step=7,
                step_unit="days",
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"{value[0]}|{value[1]}"

    dash_dcc.start_server(app)
    slider = dash_dcc.find_element(".dash-slider-root")

    dash_dcc.click_at_coord_fractions(slider, 0.49, 0.5)

    dash_dcc.wait_for_text_to_equal("#out", "2024-01-15|2024-01-29")
    assert dash_dcc.get_logs() == []


# STEP MONTHS
def test_dslsl013_step_months_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 1),
                value=date(2024, 1, 1),
                step=1,
                step_unit="months",
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"{value}"

    dash_dcc.start_server(app)
    slider = dash_dcc.find_element(".dash-slider-root")
    dash_dcc.click_at_coord_fractions(slider, 0.46, 0.5)

    dash_dcc.wait_for_text_to_equal("#out", "2024-06-01")
    assert dash_dcc.get_logs() == []


def test_dslsl014_step_months_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 1),
                value=[date(2024, 1, 1), date(2024, 12, 1)],
                step=1,
                step_unit="months",
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"{value[0]}|{value[1]}"

    dash_dcc.start_server(app)
    slider = dash_dcc.find_element(".dash-slider-root")
    dash_dcc.click_at_coord_fractions(slider, 0.46, 0.5)

    dash_dcc.wait_for_text_to_equal("#out", "2024-06-01|2024-12-01")
    assert dash_dcc.get_logs() == []


# DISABLED DATES INDICATOR SHOWN
def test_dslsl015_disabled_dates_indicator_rendered_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 1, 1),
                disabled_dates=[date(2024, 6, 15)],
                disabled_dates_indicator=True,
            ),
            html.Div(id="out"),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-disabled-range")

    indicators = dash_dcc.find_elements(".dash-slider-disabled-range")
    assert len(indicators) >= 1
    assert dash_dcc.get_logs() == []


def test_dslsl016_disabled_dates_indicator_rendered_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 1, 1), date(2024, 12, 31)],
                disabled_dates=[date(2024, 6, 15)],
                disabled_dates_indicator=True,
            ),
            html.Div(id="out"),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-disabled-range")

    indicators = dash_dcc.find_elements(".dash-slider-disabled-range")
    assert len(indicators) >= 1
    assert dash_dcc.get_logs() == []


# DISABLED DATES INDICATOR HIDDEN
def test_dslsl017_disabled_dates_indicator_hidden_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 1, 1),
                disabled_dates=[date(2024, 6, 15)],
                disabled_dates_indicator=False,
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-thumb")

    indicators = dash_dcc.find_elements(".dash-slider-disabled-range")
    assert len(indicators) == 0
    assert dash_dcc.get_logs() == []


def test_dslsl018_disabled_dates_indicator_hidden_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 1, 1), date(2024, 12, 31)],
                disabled_dates=[date(2024, 6, 15)],
                disabled_dates_indicator=False,
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-thumb")

    indicators = dash_dcc.find_elements(".dash-slider-disabled-range")
    assert len(indicators) == 0
    assert dash_dcc.get_logs() == []


# DIRECT INPUT (TRUE)
def test_dslsl019_allow_direct_input_true_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 3, 1),
                allow_direct_input=True,
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-range-slider-min-input")

    min_input = dash_dcc.find_elements(".dash-range-slider-min-input")
    assert len(min_input) == 1, "Expected one date input"
    assert dash_dcc.get_logs() == []


def test_dslsl020_allow_direct_input_true_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 3, 1), date(2024, 9, 1)],
                allow_direct_input=True,
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-range-slider-min-input")

    min_input = dash_dcc.find_elements(".dash-range-slider-min-input")
    max_input = dash_dcc.find_elements(".dash-range-slider-max-input")
    assert len(min_input) == 1, "Expected one min-date input"
    assert len(max_input) == 1, "Expected one max-date input"
    assert dash_dcc.get_logs() == []


# DIRECT INPUT (FALSE)
def test_dslsl021_allow_direct_input_false_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 3, 1),
                allow_direct_input=False,
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-thumb")

    min_input = dash_dcc.find_elements(".dash-range-slider-min-input")
    assert len(min_input) == 0, "Expected no date input"
    assert dash_dcc.get_logs() == []


def test_dslsl022_allow_direct_input_false_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 3, 1), date(2024, 9, 1)],
                allow_direct_input=False,
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-thumb")

    min_input = dash_dcc.find_elements(".dash-range-slider-min-input")
    max_input = dash_dcc.find_elements(".dash-range-slider-max-input")
    assert len(min_input) == 0, "Expected no min-date input"
    assert len(max_input) == 0, "Expected no max-date input"
    assert dash_dcc.get_logs() == []


# VERTICAL
def test_dslsl023_vertical_renders_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 3, 1),
                vertical=True,
                verticalHeight=400,
            ),
            html.Div(id="out"),
        ],
        style={"height": "600px"},
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"Selected: {value}"

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal(
        "#out",
        f"Selected: {date(2024, 3, 1)}",
    )
    assert dash_dcc.get_logs() == []


def test_dslsl024_vertical_renders_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 3, 1), date(2024, 9, 1)],
                vertical=True,
                verticalHeight=400,
            ),
            html.Div(id="out"),
        ],
        style={"height": "600px"},
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"{value[0]} to {value[1]}"

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal(
        "#out",
        f"{date(2024, 3, 1)} to {date(2024, 9, 1)}",
    )
    assert dash_dcc.get_logs() == []


# LOADING STATE
def test_dslsl025_loading_state_slider(dash_dcc):
    lock = Lock()

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Trigger", id="btn"),
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 6, 15),
            ),
        ]
    )

    @app.callback(Output("slider", "value"), Input("btn", "n_clicks"))
    def cb(_):
        with lock:
            return date(2024, 8, 20)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".date-slider-container")

    with lock:
        dash_dcc.find_element("#btn").click()
        dash_dcc.wait_for_element(
            '[data-dash-is-loading="true"]',
            timeout=4,
        )

    dash_dcc.wait_for_no_elements('[data-dash-is-loading="true"]')
    assert dash_dcc.get_logs() == []


def test_dslsl026_loading_state_rangeslider(dash_dcc):
    lock = Lock()

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Trigger", id="btn"),
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 3, 1), date(2024, 9, 1)],
            ),
        ]
    )

    @app.callback(Output("slider", "value"), Input("btn", "n_clicks"))
    def cb(_):
        with lock:
            return [date(2024, 4, 1), date(2024, 10, 1)]

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-date-range-slider-wrapper")

    with lock:
        dash_dcc.find_element("#btn").click()
        dash_dcc.wait_for_element(
            '[data-dash-is-loading="true"]',
            timeout=4,
        )

    dash_dcc.wait_for_no_elements('[data-dash-is-loading="true"]')
    assert dash_dcc.get_logs() == []


# EXPLICIT MARKS
def test_dslsl027_explicit_marks_render_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 1, 1),
                marks={
                    str(date(2024, 1, 1)): "Jan",
                    str(date(2024, 4, 1)): "Apr",
                    str(date(2024, 7, 1)): "Jul",
                    str(date(2024, 10, 1)): "Oct",
                    str(date(2024, 12, 31)): "Dec",
                },
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-mark")

    marks = dash_dcc.find_elements(".dash-slider-mark")
    texts = [m.text for m in marks]

    assert texts == [
        "Jan",
        "Apr",
        "Jul",
        "Oct",
        "Dec",
    ]
    assert dash_dcc.get_logs() == []


def test_dslsl028_explicit_marks_render_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 1, 1), date(2024, 12, 31)],
                marks={
                    str(date(2024, 1, 1)): "Jan",
                    str(date(2024, 4, 1)): "Apr",
                    str(date(2024, 7, 1)): "Jul",
                    str(date(2024, 10, 1)): "Oct",
                    str(date(2024, 12, 31)): "Dec",
                },
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-mark")

    marks = dash_dcc.find_elements(".dash-slider-mark")
    texts = [m.text for m in marks]

    assert texts == [
        "Jan",
        "Apr",
        "Jul",
        "Oct",
        "Dec",
    ]
    assert dash_dcc.get_logs() == []


# AUTO MARKS
def test_dslsl029_auto_marks_render_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 1, 1),
                step=1,
                step_unit="months",
            ),
        ],
        style={"width": "800px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-mark")

    marks = dash_dcc.find_elements(".dash-slider-mark")
    assert len(marks) >= 2
    assert dash_dcc.get_logs() == []


def test_dslsl030_auto_marks_render_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 1, 1), date(2024, 12, 31)],
                step=1,
                step_unit="months",
            ),
        ],
        style={"width": "800px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-slider-mark")

    marks = dash_dcc.find_elements(".dash-slider-mark")
    assert len(marks) >= 2, f"Expected at least 2 auto marks, got {len(marks)}"
    assert dash_dcc.get_logs() == []


# DIRECT INPUT
def test_dslsl031_direct_input_updates_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 5, 10),
                allow_direct_input=True,
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"Date: {value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(1200, 600)
    dash_dcc.wait_for_text_to_equal("#out", "Date: 2024-05-10")

    input_container = dash_dcc.find_element(".dash-range-slider-min-input")
    inner_input = input_container.find_element("tag name", "input")

    inner_input.clear()
    inner_input.send_keys("2024-08-20")
    inner_input.send_keys("\n")

    dash_dcc.wait_for_text_to_equal("#out", "Date: 2024-08-20")
    assert dash_dcc.get_logs() == []


def test_dslsl032_direct_input_updates_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 3, 1), date(2024, 9, 1)],
                allow_direct_input=True,
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("slider", "value"))
    def cb(value):
        return f"{value[0]} to {value[1]}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(1200, 600)
    dash_dcc.wait_for_text_to_equal("#out", "2024-03-01 to 2024-09-01")

    min_input_container = dash_dcc.find_element(".dash-range-slider-min-input")
    inner_input = min_input_container.find_element("tag name", "input")

    inner_input.clear()
    inner_input.send_keys("2024-04-15")
    inner_input.send_keys("\n")

    dash_dcc.wait_for_text_to_equal("#out", "2024-04-15 to 2024-09-01")
    assert dash_dcc.get_logs() == []


# RESIZING
def test_dslsl033_resize_hides_inputs_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=date(2024, 5, 10),
                allow_direct_input=True,
            ),
        ]
    )

    import time

    dash_dcc.start_server(app)

    # Large Window
    dash_dcc.driver.set_window_size(1200, 600)

    # Check if inputs are visible
    for _ in range(10):
        try:
            elem = dash_dcc.find_element(".dash-range-slider-min-input")
            if elem.value_of_css_property("display") != "none":
                break
        except Exception:
            pass
        time.sleep(0.2)

    # Small Window
    dash_dcc.driver.set_window_size(300, 600)

    # Check if inputs are visible
    for _ in range(10):
        try:
            elem = dash_dcc.find_element(".dash-range-slider-min-input")
            if elem.value_of_css_property("display") == "none":
                break
        except Exception:
            break
        time.sleep(0.2)

    assert dash_dcc.get_logs() == []


def test_dslsl034_resize_hides_inputs_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateRangeSlider(
                id="slider",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                value=[date(2024, 3, 1), date(2024, 9, 1)],
                allow_direct_input=True,
            ),
        ]
    )

    dash_dcc.start_server(app)

    # Large Window
    dash_dcc.driver.set_window_size(1200, 600)

    # Check if inputs are visible
    for _ in range(10):
        try:
            min_elem = dash_dcc.find_element(".dash-range-slider-min-input")
            max_elem = dash_dcc.find_element(".dash-range-slider-max-input")
            if (
                min_elem.value_of_css_property("display") != "none"
                and max_elem.value_of_css_property("display") != "none"
            ):
                break
        except Exception:
            pass
        time.sleep(0.2)

    # Small Window
    dash_dcc.driver.set_window_size(300, 600)

    # Check if inputs are visible
    for _ in range(10):
        try:
            min_elem = dash_dcc.find_element(".dash-range-slider-min-input")
            max_elem = dash_dcc.find_element(".dash-range-slider-max-input")
            if (
                min_elem.value_of_css_property("display") == "none"
                and max_elem.value_of_css_property("display") == "none"
            ):
                break
        except Exception:
            break
        time.sleep(0.2)

    assert dash_dcc.get_logs() == []
