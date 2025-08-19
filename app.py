from multiprocessing import Lock, Value

from dash import (
    Dash,
    Input,
    Output,
    html,
    # dcc,
    dcc_refresh as dcc,
)

lock = Lock()

app = Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.Label([
            html.P("DatePicker"),
            dcc.DatePickerRange(id="dpr", clearable=True),
            dcc.DatePickerSingle(id="dps", clearable=True),
        ]),
        html.Label([
            html.P("Slider"),
            dcc.Slider(
                min=0,
                max=100,
                marks={0: '0', 15: '15', 25: '25', 50: '50', 75: '75', 100: '100'},
                value=75,
                id="slider",
                # tooltip={"always_visible": True, "transform": "transformTooltip"},
            ),
        ]),
        html.Label([
            html.P("Vertical Range Slider"),
            dcc.RangeSlider(
                id="vertical-range-slider",
                min=0,
                max=9,
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                value=[4, 6],
                vertical=True,
                verticalHeight=300,
            ),

        ]),
        html.Label([
            html.P("Range Slider"),
            dcc.RangeSlider(
                min=0,
                max=100,
                step=1,
                id="range-slider",
                marks={0: '0', 15: '15', 25: '25', 50: '50', 75: '75', 100: '100'},
                value=[25, 75]
            ),
        ]),
        html.Label([
            html.P("Vertical Slider"),
            dcc.Slider(
                id="vertical-slider",
                vertical=True,
                min=0,
                max=5,
                value=3,
                marks={i: f"Label {i}" for i in range(-1, 10)}
            )
        ], style={"width": "300px", "display": "block"}),

        html.Div(id="slider1"),
        html.Div(id="slider2"),
        html.Label([
            html.P("Text"),
            dcc.Input(id="input", value="initial value", debounce=True, type=None),
        ]),
        html.Label([
            html.P("Text"),
            dcc.Input(id="disabled", value="initial value", disabled=True),
        ]),
        html.Label([
            html.P("Number"),
            dcc.Input(id="number", value=17, type="number", min=10, max=23),
        ]),
        html.Label([
            html.P("Password"),
            dcc.Input(id="password", value=17, type="password", minLength=10),
        ]),
        html.Label([
            html.P("Email"),
            dcc.Input(id="email", type="email"),
        ]),
        html.Label([
            html.P("Range"),
            dcc.Input(id="range", type="range"),
        ]),
        html.Label([
            html.P("Search"),
            dcc.Input(id="search", type="search"),
        ]),
        html.Label([
            html.P("Tel"),
            dcc.Input(id="tel", type="tel"),
        ]),
        html.Label([
            html.P("URL"),
            dcc.Input(id="url", type="url"),
        ]),
        html.Label([
            html.P("Hidden"),
            dcc.Input(id="hidden", type="hidden"),
        ]),
        html.Div(id="output-1"),
    ]
)
call_count = Value("i", 0)


@app.callback(Output("slider1", "children"), [Input("vertical-slider", "drag_value")])
def update_drag_value(value):
    return f"Slider drag_value: {value}"

@app.callback(Output("slider2", "children"), [Input("vertical-slider", "value")])
def update_value(value):
    return f"Slider value: {value}"

app.clientside_callback(
    """
        function(value) {
            //alert(value);
        }
    """,
    Input("input", "value"),
)


if __name__ == "__main__":
    app.run(debug=True, port=8051)
