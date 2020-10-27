import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc


def test_slsl001_always_visible_slider(dash_dcc):
    app = dash.Dash(__name__)
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
        return "You have selected {}".format(value)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 5")

    slider = dash_dcc.find_element("#slider")
    dash_dcc.click_at_coord_fractions(slider, 0.5, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 10")
    dash_dcc.click_at_coord_fractions(slider, 0.75, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 15")


def test_slsl002_always_visible_rangeslider(dash_dcc):
    app = dash.Dash(__name__)
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
        return "You have selected {}-{}".format(*rng)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 5-15")

    slider = dash_dcc.find_element("#rangeslider")
    dash_dcc.click_at_coord_fractions(slider, 0.15, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 2-15")
    dash_dcc.click_at_coord_fractions(slider, 0.5, 0.25)
    dash_dcc.wait_for_text_to_equal("#out", "You have selected 2-10")


def test_slsl003_out_of_range_marks_slider(dash_dcc):

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Slider(
                min=0, max=5, marks={i: "Label {}".format(i) for i in range(-1, 10)}
            )
        ]
    )

    dash_dcc.start_server(app)

    assert len(dash_dcc.find_elements("span.rc-slider-mark-text")) == 6


def test_slsl004_out_of_range_marks_rangeslider(dash_dcc):

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RangeSlider(
                min=0, max=5, marks={i: "Label {}".format(i) for i in range(-1, 10)}
            )
        ]
    )

    dash_dcc.start_server(app)

    assert len(dash_dcc.find_elements("span.rc-slider-mark-text")) == 6


def test_slsl005_slider_tooltip(dash_dcc):
    app = dash.Dash(__name__)
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
                style=dict(maxHeight=300, overflowX="scroll"),
            )
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#test-slider")
    dash_dcc.percy_snapshot(
        "slider-make sure tooltips are only visible if parent slider is visible"
    )
