import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

import dash_table
from index import app


def layout():
    return html.Div(
        className="row",
        children=[
            html.Div(
                className="eight columns",
                children=html.Div(id="table-container"),
            ),
            html.Div(
                className="four columns",
                children=[
                    html.Label("Editable"),
                    dcc.RadioItems(
                        id="editable",
                        options=[
                            {"label": str(i), "value": i} for i in [True, False]
                        ],
                        value=True,
                    ),
                    html.Label("Sorting"),
                    dcc.RadioItems(
                        id="sorting",
                        options=[
                            {"label": str(i), "value": i}
                            for i in ["fe", True, False]
                        ],
                        value=True,
                    ),
                    html.Label("Sorting Type"),
                    dcc.RadioItems(
                        id="sorting_type",
                        options=[
                            {"label": str(i), "value": i}
                            for i in ["single", "multi"]
                        ],
                        value="single",
                    ),
                    html.Label("Sorting Treat Empty String As None"),
                    dcc.RadioItems(
                        id="sorting_treat_empty_string_as_none",
                        options=[
                            {"label": str(i), "value": i} for i in [True, False]
                        ],
                        value=True,
                    ),
                    html.Label("Row Selectable"),
                    dcc.RadioItems(
                        id="row_selectable",
                        options=[
                            {"label": str(i), "value": i}
                            for i in ["single", "multi"]
                        ],
                        value="single",
                    ),
                    html.Label("Virtualization"),
                    dcc.RadioItems(
                        id="virtualization",
                        options=[
                            {"label": str(i), "value": i}
                            for i in ["fe", True, False]
                        ],
                        value="fe",
                    ),
                    html.Label("Number of Fixed Rows"),
                    dcc.Input(id="n_fixed_rows", type="number", value="0"),
                    html.Label("Number of Fixed Columns"),
                    dcc.Input(id="n_fixed_columns", type="number", value="0"),
                ],
            ),
        ],
    )


@app.callback(
    Output("table-container", "children"),
    [
        Input(prop, "value")
        for prop in [
            "editable",  # 0
            "sorting",  # 1
            "sorting_type",  # 2
            "sorting_treat_empty_string_as_none",  # 3
            "row_selectable",  # 4
            "virtualization",  # 5
            "n_fixed_rows",  # 6
            "n_fixed_columns",
        ]
    ],
)
def update_table(*args):
    df = pd.read_csv("./datasets/gapminder.csv")
    return dash_table.Table(
        id=__name__,
        columns=[{"name": i, "id": i} for i in df.columns],
        dataframe=df.to_dict("rows"),
        editable=args[0],
        sorting=args[1],
        sorting_type=args[2],
        sorting_treat_empty_string_as_none=args[3],
        row_selectable=args[4],
        virtualization=args[5],
        n_fixed_rows=args[6],
        n_fixed_columns=args[7],
    )
