from multiprocessing import Lock
from dash import Dash, Input, Output, dcc, html


def test_slsl001_always_visible_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Slider(
                id="slider",
                min=0,
                max=20,
                step=1,
                value=5,
                tooltip={"always_visible": True},
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), [Input("slider", "value")])
    def update_output(value):
        return f"You have selected {value}"

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 5")

    slider = dash_dcc.find_element("#slider")
    dash_dcc.click_at_coord_fractions(slider, 0.5, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 10")
    dash_dcc.click_at_coord_fractions(slider, 0.75, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 15")

    assert dash_dcc.get_logs() == []


def test_slsl002_always_visible_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "400px"},
        children=[
            dcc.RangeSlider(
                id="rangeslider",
                min=0,
                max=20,
                step=1,
                value=[5, 15],
                tooltip={"always_visible": True},
            ),
            html.Div(id="out"),
        ],
    )

    @app.callback(Output("out", "children"), [Input("rangeslider", "value")])
    def update_output(rng):
        return f"You have selected {rng[0]}-{rng[1]}"

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 5-15")

    slider = dash_dcc.find_element("#rangeslider")
    dash_dcc.click_at_coord_fractions(slider, 0.15, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 2-15")
    dash_dcc.click_at_coord_fractions(slider, 0.5, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 2-10")

    assert dash_dcc.get_logs() == []


def test_slsl003_out_of_range_marks_slider(dash_dcc):

    app = Dash(__name__)
    app.layout = html.Div(
        [dcc.Slider(min=0, max=5, marks={i: f"Label {i}" for i in range(-1, 10)})]
    )

    dash_dcc.start_server(app)

    assert len(dash_dcc.find_elements("span.rc-slider-mark-text")) == 6

    assert dash_dcc.get_logs() == []


def test_slsl004_out_of_range_marks_rangeslider(dash_dcc):

    app = Dash(__name__)
    app.layout = html.Div(
        [dcc.RangeSlider(min=0, max=5, marks={i: f"Label {i}" for i in range(-1, 10)})]
    )

    dash_dcc.start_server(app)

    assert len(dash_dcc.find_elements("span.rc-slider-mark-text")) == 6

    assert dash_dcc.get_logs() == []


def test_slsl005_slider_tooltip(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        dcc.Slider(
                            min=0,
                            max=100,
                            value=65,
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100),
                    ),
                    html.Div(
                        dcc.Slider(
                            min=0,
                            max=100,
                            value=65,
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100),
                    ),
                    html.Div(
                        dcc.Slider(
                            min=0,
                            max=100,
                            value=65,
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100),
                    ),
                    html.Div(
                        dcc.Slider(
                            min=0,
                            max=100,
                            value=65,
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100),
                    ),
                    html.Div(
                        dcc.Slider(
                            id="test-slider",
                            min=0,
                            max=100,
                            value=65,
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100),
                    ),
                ],
                style=dict(maxHeight=300, overflowX="scroll", width=400),
            )
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#test-slider")
    dash_dcc.percy_snapshot(
        "slider-make sure tooltips are only visible if parent slider is visible"
    )

    assert dash_dcc.get_logs() == []


def test_slsl006_rangeslider_tooltip(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        dcc.RangeSlider(
                            min=0,
                            max=100,
                            value=[0, 65],
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100, marginTop=25),
                    ),
                    html.Div(
                        dcc.RangeSlider(
                            min=0,
                            max=100,
                            value=[0, 65],
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100),
                    ),
                    html.Div(
                        dcc.RangeSlider(
                            min=0,
                            max=100,
                            value=[0, 65],
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100),
                    ),
                    html.Div(
                        dcc.RangeSlider(
                            min=0,
                            max=100,
                            value=[0, 65],
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100),
                    ),
                    html.Div(
                        dcc.RangeSlider(
                            id="test-slider",
                            min=0,
                            max=100,
                            value=[0, 65],
                            tooltip={"always_visible": True, "placement": "top"},
                        ),
                        style=dict(height=100),
                    ),
                ],
                style=dict(
                    maxHeight=300,
                    overflowX="scroll",
                    backgroundColor="#edf9f7",
                    width=400,
                ),
            )
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#test-slider")
    dash_dcc.percy_snapshot("slsl006- dcc.RangeSlider tooltip position")


def test_slsl007_drag_value_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Slider(
                id="slider",
                min=0,
                max=20,
                step=1,
                value=5,
                tooltip={"always_visible": True},
            ),
            html.Div(id="out-value"),
            html.Div(id="out-drag-value"),
        ]
    )

    @app.callback(Output("out-drag-value", "children"), [Input("slider", "drag_value")])
    def update_output1(value):
        return f"You have dragged {value}"

    @app.callback(Output("out-value", "children"), [Input("slider", "value")])
    def update_output2(value):
        return f"You have selected {value}"

    dash_dcc.start_server(app)
    slider = dash_dcc.find_element("#slider")

    dash_dcc.wait_for_text_to_equal("#out-value", "You have selected 5")
    dash_dcc.wait_for_text_to_equal("#out-drag-value", "You have dragged 5")

    dash_dcc.click_and_hold_at_coord_fractions(slider, 0.25, 0.25)
    dash_dcc.move_to_coord_fractions(slider, 0.75, 0.25)
    dash_dcc.wait_for_text_to_equal("#out-drag-value", "You have dragged 15")
    dash_dcc.move_to_coord_fractions(slider, 0.5, 0.25)
    dash_dcc.wait_for_text_to_equal("#out-drag-value", "You have dragged 10")
    dash_dcc.wait_for_text_to_equal("#out-value", "You have selected 5")
    dash_dcc.release()
    dash_dcc.wait_for_text_to_equal("#out-value", "You have selected 10")

    assert dash_dcc.get_logs() == []


def test_slsl008_drag_value_rangeslider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RangeSlider(
                id="slider",
                min=0,
                max=20,
                step=1,
                value=(5, 15),
                tooltip={"always_visible": True},
            ),
            html.Div(id="out-value"),
            html.Div(id="out-drag-value"),
        ]
    )

    @app.callback(Output("out-drag-value", "children"), [Input("slider", "drag_value")])
    def update_output1(value):
        value = value or (None, None)
        return f"You have dragged {value[0]}-{value[1]}"

    @app.callback(Output("out-value", "children"), [Input("slider", "value")])
    def update_output2(value):
        return f"You have selected {value[0]}-{value[1]}"

    dash_dcc.start_server(app)
    slider = dash_dcc.find_element("#slider")

    dash_dcc.wait_for_text_to_equal("#out-value", "You have selected 5-15")
    dash_dcc.wait_for_text_to_equal("#out-drag-value", "You have dragged 5-15")

    dash_dcc.click_and_hold_at_coord_fractions(slider, 0.25, 0.25)
    dash_dcc.move_to_coord_fractions(slider, 0.5, 0.25)
    dash_dcc.wait_for_text_to_equal("#out-drag-value", "You have dragged 10-15")
    dash_dcc.wait_for_text_to_equal("#out-value", "You have selected 5-15")
    dash_dcc.release()
    dash_dcc.wait_for_text_to_equal("#out-value", "You have selected 10-15")

    assert dash_dcc.get_logs() == []


def test_slsl009_loading_state(dash_dcc):
    lock = Lock()

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="test-btn"),
            html.Label(id="test-div", children=["Horizontal Slider"]),
            dcc.Slider(
                id="horizontal-slider",
                min=0,
                max=9,
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                value=5,
            ),
        ]
    )

    @app.callback(Output("horizontal-slider", "value"), [Input("test-btn", "n_clicks")])
    def user_delayed_value(n_clicks):
        with lock:
            return 5

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.wait_for_element('#horizontal-slider[data-dash-is-loading="true"]')

    dash_dcc.wait_for_element('#horizontal-slider:not([data-dash-is-loading="true"])')

    with lock:
        dash_dcc.wait_for_element("#test-btn").click()
        dash_dcc.wait_for_element('#horizontal-slider[data-dash-is-loading="true"]')

    dash_dcc.wait_for_element('#horizontal-slider:not([data-dash-is-loading="true"])')
    assert dash_dcc.get_logs() == []


def test_slsl010_range_loading_state(dash_dcc):
    lock = Lock()

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="test-btn"),
            html.Label(id="test-div", children=["Horizontal Range Slider"]),
            dcc.RangeSlider(
                id="horizontal-range-slider",
                min=0,
                max=9,
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                value=[4, 6],
            ),
        ]
    )

    @app.callback(
        Output("horizontal-range-slider", "value"), [Input("test-btn", "n_clicks")]
    )
    def delayed_value(children):
        with lock:
            return [4, 6]

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.wait_for_element(
            '#horizontal-range-slider[data-dash-is-loading="true"]'
        )

    dash_dcc.wait_for_element(
        '#horizontal-range-slider:not([data-dash-is-loading="true"])'
    )

    with lock:
        dash_dcc.wait_for_element("#test-btn").click()
        dash_dcc.wait_for_element(
            '#horizontal-range-slider[data-dash-is-loading="true"]'
        )

    dash_dcc.wait_for_element(
        '#horizontal-range-slider:not([data-dash-is-loading="true"])'
    )
    assert dash_dcc.get_logs() == []


def test_slsl011_horizontal_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Horizontal Slider"),
            dcc.Slider(
                id="horizontal-slider",
                min=0,
                max=9,
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                value=5,
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#horizontal-slider")
    dash_dcc.percy_snapshot("horizontal slider")

    dash_dcc.wait_for_element('#horizontal-slider div[role="slider"]').click()
    assert dash_dcc.get_logs() == []


def test_slsl012_vertical_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Vertical Slider"),
            dcc.Slider(
                id="vertical-slider",
                min=0,
                max=9,
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                value=5,
                vertical=True,
            ),
        ],
        style={"height": "500px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#vertical-slider")
    dash_dcc.percy_snapshot("vertical slider")

    dash_dcc.wait_for_element('#vertical-slider div[role="slider"]').click()
    assert dash_dcc.get_logs() == []


def test_slsl013_horizontal_range_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Horizontal Range Slider"),
            dcc.RangeSlider(
                id="horizontal-range-slider",
                min=0,
                max=9,
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                value=[4, 6],
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#horizontal-range-slider")
    dash_dcc.percy_snapshot("horizontal range slider")

    dash_dcc.wait_for_element(
        '#horizontal-range-slider div.rc-slider-handle-1[role="slider"]'
    ).click()
    dash_dcc.wait_for_element(
        '#horizontal-range-slider div.rc-slider-handle-2[role="slider"]'
    ).click()
    assert dash_dcc.get_logs() == []


def test_slsl014_vertical_range_slider(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Vertical Range Slider"),
            dcc.RangeSlider(
                id="vertical-range-slider",
                min=0,
                max=9,
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                value=[4, 6],
                vertical=True,
            ),
        ],
        style={"height": "500px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#vertical-range-slider")
    dash_dcc.percy_snapshot("vertical range slider")

    dash_dcc.wait_for_element(
        '#vertical-range-slider div.rc-slider-handle-1[role="slider"]'
    ).click()
    dash_dcc.wait_for_element(
        '#vertical-range-slider div.rc-slider-handle-2[role="slider"]'
    ).click()
    assert dash_dcc.get_logs() == []


def test_slsl015_range_slider_step_none(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Steps = Marks Slider"),
            dcc.Slider(
                id="none-step-slider",
                min=0,
                max=6,
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                step=None,
                value=4.6,
                vertical=False,
            ),
        ],
        style={"height": "500px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#none-step-slider")
    dash_dcc.percy_snapshot("none step slider")

    dash_dcc.wait_for_element(
        '#none-step-slider div.rc-slider-handle[aria-valuenow="5"]'
    )

    assert dash_dcc.get_logs() == []


def test_slsl015_range_slider_no_min_max(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("No Min or Max Slider"),
            dcc.Slider(
                id="no-min-max-step-slider",
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                step=None,
                value=5,
                vertical=False,
            ),
        ],
        style={"height": "500px"},
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#no-min-max-step-slider")
    dash_dcc.percy_snapshot("no-min-max step slider")

    dash_dcc.wait_for_element(
        '#no-min-max-step-slider div.rc-slider-handle[aria-valuemax="5"]'
    )

    assert dash_dcc.get_logs() == []
