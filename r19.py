"""
React 19 test app with most Dash components.
Run with: python r19.py
"""

import os
os.environ["REACT_VERSION"] = "19.2.0"

from dash import Dash, html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import pandas as pd

# Sample data
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Grapes", "Strawberries"],
    "Amount": [4, 2, 5, 3, 6],
    "City": ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
})

app = Dash(__name__)

app.layout = html.Div([
    html.H1("React 19 Component Test"),
    html.P(f"Running React version: {os.environ.get('REACT_VERSION')}"),

    html.Hr(),
    html.H2("Core HTML Components"),
    html.Div([
        html.Button("Click Me", id="button", n_clicks=0),
        html.Span(" Clicks: ", style={"marginLeft": "10px"}),
        html.Span(id="click-output", children="0"),
    ]),

    html.Hr(),
    html.H2("Input Components"),
    html.Div([
        html.Label("Text Input:"),
        dcc.Input(id="text-input", type="text", placeholder="Type something...", debounce=True),
        html.Div(id="text-output"),
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.Label("Dropdown:"),
        dcc.Dropdown(
            id="dropdown",
            options=[{"label": f, "value": f} for f in df["Fruit"]],
            value="Apples",
            clearable=True,
        ),
        html.Div(id="dropdown-output"),
    ], style={"marginBottom": "20px", "width": "300px"}),

    html.Div([
        html.Label("Multi-Select Dropdown:"),
        dcc.Dropdown(
            id="multi-dropdown",
            options=[{"label": f, "value": f} for f in df["Fruit"]],
            value=["Apples", "Oranges"],
            multi=True,
        ),
    ], style={"marginBottom": "20px", "width": "300px"}),

    html.Div([
        html.Label("Slider:"),
        dcc.Slider(id="slider", min=0, max=10, step=1, value=5, marks={i: str(i) for i in range(11)}),
        html.Div(id="slider-output"),
    ], style={"marginBottom": "20px", "width": "400px"}),

    html.Div([
        html.Label("Range Slider:"),
        dcc.RangeSlider(id="range-slider", min=0, max=100, step=10, value=[20, 80]),
    ], style={"marginBottom": "20px", "width": "400px"}),

    html.Div([
        html.Label("Radio Items:"),
        dcc.RadioItems(
            id="radio",
            options=[{"label": c, "value": c} for c in df["City"]],
            value="NYC",
            inline=True,
        ),
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.Label("Checklist:"),
        dcc.Checklist(
            id="checklist",
            options=[{"label": c, "value": c} for c in df["City"]],
            value=["NYC", "LA"],
            inline=True,
        ),
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.Label("Date Picker:"),
        dcc.DatePickerSingle(id="date-picker", date="2024-01-15"),
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.Label("Date Range Picker:"),
        dcc.DatePickerRange(
            id="date-range",
            start_date="2024-01-01",
            end_date="2024-12-31",
        ),
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.Label("Textarea:"),
        dcc.Textarea(id="textarea", value="Some text here...", style={"width": "300px", "height": "100px"}),
    ], style={"marginBottom": "20px"}),

    html.Hr(),
    html.H2("Graph Component"),
    dcc.Graph(
        id="graph",
        figure=px.bar(df, x="Fruit", y="Amount", color="City", title="Fruit Amounts by City")
    ),

    html.Hr(),
    html.H2("DataTable"),
    dash_table.DataTable(
        id="table",
        columns=[{"name": c, "id": c} for c in df.columns],
        data=df.to_dict("records"),
        editable=True,
        filter_action="native",
        sort_action="native",
        row_selectable="multi",
        page_size=10,
    ),

    html.Hr(),
    html.H2("Tabs"),
    dcc.Tabs(id="tabs", value="tab-1", children=[
        dcc.Tab(label="Tab 1", value="tab-1", children=[
            html.Div("Content for Tab 1", style={"padding": "20px"})
        ]),
        dcc.Tab(label="Tab 2", value="tab-2", children=[
            html.Div("Content for Tab 2", style={"padding": "20px"})
        ]),
    ]),

    html.Hr(),
    html.H2("Loading Component"),
    dcc.Loading(
        id="loading",
        type="circle",
        children=html.Div(id="loading-output", children="Content loaded!")
    ),

    html.Hr(),
    html.H2("Markdown"),
    dcc.Markdown("""
    ### This is Markdown

    - Item 1
    - Item 2
    - **Bold text**
    - *Italic text*

    ```python
    def hello():
        return "Hello, React 19!"
    ```
    """),

    html.Hr(),
    html.H2("Store & Interval"),
    dcc.Store(id="store", data={"count": 0}),
    dcc.Interval(id="interval", interval=5000, n_intervals=0, disabled=True),
    html.Div(id="interval-output", children="Interval disabled"),

    html.Hr(),
    html.H2("Clipboard"),
    dcc.Clipboard(id="clipboard", target_id="text-input", style={"fontSize": "20px"}),

    html.Hr(),
    html.H2("Tooltip"),
    html.Div([
        html.Span("Hover over the graph points to see tooltips", style={"fontStyle": "italic"}),
    ]),

    html.Br(),
    html.Br(),
], style={"padding": "20px", "maxWidth": "800px", "margin": "0 auto"})


@callback(
    Output("click-output", "children"),
    Input("button", "n_clicks")
)
def update_clicks(n):
    return str(n)


@callback(
    Output("text-output", "children"),
    Input("text-input", "value")
)
def update_text(value):
    return f"You typed: {value}" if value else ""


@callback(
    Output("dropdown-output", "children"),
    Input("dropdown", "value")
)
def update_dropdown(value):
    return f"Selected: {value}" if value else "Nothing selected"


@callback(
    Output("slider-output", "children"),
    Input("slider", "value")
)
def update_slider(value):
    return f"Slider value: {value}"


if __name__ == "__main__":
    app.run(debug=True, port=8050)
