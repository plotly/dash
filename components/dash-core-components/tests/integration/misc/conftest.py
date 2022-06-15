# -*- coding: utf-8 -*-
from datetime import datetime
import pytest
from dash import Dash, dcc, html


OPTIONS = [
    {"label": "New York City", "value": "NYC"},
    {"label": "Montréal", "value": "MTL"},
    {"label": "San Francisco", "value": "SF"},
    {"label": "北京", "value": "帝都"},
    {"label": "臺北", "value": "天龍國"},
]


@pytest.fixture(scope="module")
def platter_app():
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div(id="waitfor"),
            html.Label("Upload"),
            dcc.Upload(),
            html.Label("Horizontal Tabs"),
            dcc.Tabs(
                id="tabs",
                children=[
                    dcc.Tab(
                        label="Tab one",
                        className="test",
                        style={"border": "1px solid magenta"},
                        children=[html.Div(["Test"])],
                    ),
                    dcc.Tab(
                        label="Tab two",
                        children=[
                            html.Div(
                                [
                                    html.H1("This is the content in tab 2"),
                                    html.P("A graph here would be nice!"),
                                ]
                            )
                        ],
                        id="tab-one",
                    ),
                    dcc.Tab(
                        label="Tab three",
                        children=[html.Div([html.H1("This is the content in tab 3")])],
                    ),
                ],
                style={"fontFamily": "system-ui"},
                content_style={"border": "1px solid #d6d6d6", "padding": "44px"},
                parent_style={"maxWidth": "1000px", "margin": "0 auto"},
            ),
            html.Label("Vertical Tabs"),
            dcc.Tabs(
                id="tabs1",
                vertical=True,
                children=[
                    dcc.Tab(label="Tab one", children=[html.Div(["Test"])]),
                    dcc.Tab(
                        label="Tab two",
                        children=[
                            html.Div(
                                [
                                    html.H1("This is the content in tab 2"),
                                    html.P("A graph here would be nice!"),
                                ]
                            )
                        ],
                    ),
                    dcc.Tab(
                        label="Tab three",
                        children=[html.Div([html.H1("This is the content in tab 3")])],
                    ),
                ],
            ),
            html.Label("Dropdown"),
            dcc.Dropdown(options=OPTIONS, value="MTL", id="dropdown"),
            html.Label("Multi-Select Dropdown"),
            dcc.Dropdown(options=OPTIONS, value=["MTL", "SF"], multi=True),
            html.Label("Radio Items"),
            dcc.RadioItems(options=OPTIONS, value="MTL"),
            html.Label("Checkboxes"),
            dcc.Checklist(options=OPTIONS, value=["MTL", "SF"]),
            html.Label("Text Input"),
            dcc.Input(value="", placeholder="type here", id="textinput"),
            html.Label("Disabled Text Input"),
            dcc.Input(
                value="disabled",
                type="text",
                id="disabled-textinput",
                disabled=True,
            ),
            html.Label("Slider"),
            dcc.Slider(
                min=0,
                max=9,
                marks={i: f"Label {i}" if i == 1 else str(i) for i in range(1, 6)},
                value=5,
            ),
            html.Label("Graph"),
            dcc.Graph(
                id="graph",
                figure={
                    "data": [{"x": [1, 2, 3], "y": [4, 1, 4]}],
                    "layout": {"title": "北京"},
                },
            ),
            html.Div(
                [
                    html.Label("DatePickerSingle"),
                    dcc.DatePickerSingle(
                        id="date-picker-single", date=datetime(1997, 5, 10)
                    ),
                    html.Div(
                        [
                            html.Label("DatePickerSingle - empty input"),
                            dcc.DatePickerSingle(),
                        ],
                        id="dt-single-no-date-value",
                    ),
                    html.Div(
                        [
                            html.Label(
                                "DatePickerSingle - initial visible month (May 97)"
                            ),
                            dcc.DatePickerSingle(
                                initial_visible_month=datetime(1997, 5, 10)
                            ),
                        ],
                        id="dt-single-no-date-value-init-month",
                    ),
                ]
            ),
            html.Div(
                [
                    html.Label("DatePickerRange"),
                    dcc.DatePickerRange(
                        id="date-picker-range",
                        start_date_id="startDate",
                        end_date_id="endDate",
                        start_date=datetime(1997, 5, 3),
                        end_date_placeholder_text="Select a date!",
                    ),
                    html.Div(
                        [
                            html.Label("DatePickerRange - empty input"),
                            dcc.DatePickerRange(
                                start_date_id="startDate",
                                end_date_id="endDate",
                                start_date_placeholder_text="Start date",
                                end_date_placeholder_text="End date",
                            ),
                        ],
                        id="dt-range-no-date-values",
                    ),
                    html.Div(
                        [
                            html.Label(
                                "DatePickerRange - initial visible month (May 97)"
                            ),
                            dcc.DatePickerRange(
                                start_date_id="startDate",
                                end_date_id="endDate",
                                start_date_placeholder_text="Start date",
                                end_date_placeholder_text="End date",
                                initial_visible_month=datetime(1997, 5, 10),
                            ),
                        ],
                        id="dt-range-no-date-values-init-month",
                    ),
                ]
            ),
            html.Label("TextArea"),
            dcc.Textarea(placeholder="Enter a value... 北京", style={"width": "100%"}),
            html.Label("Markdown"),
            dcc.Markdown(
                """
            #### Dash and Markdown

            Dash supports [Markdown](https://rexxars.github.io/react-markdown/).

            Markdown is a simple way to write and format text.
            It includes a syntax for things like **bold text** and *italics*,
            [links](https://rexxars.github.io/react-markdown/), inline `code` snippets, lists,
            quotes, and more.

            1. Links are auto-rendered: https://dash.plotly.com.
            2. This uses ~commonmark~ GitHub flavored markdown.

            Tables are also supported:

            | First Header  | Second Header |
            | ------------- | ------------- |
            | Content Cell  | Content Cell  |
            | Content Cell  | Content Cell  |

            北京
        """.replace(
                    "    ", ""
                )
            ),
            dcc.Markdown(["# Line one", "## Line two"]),
            dcc.Markdown(),
            dcc.Markdown(
                """
            ```py
            import python
            print(3)
            ```"""
            ),
            dcc.Markdown(["```py", "import python", "print(3)", "```"]),
            dcc.Markdown(),
        ]
    )

    yield app
