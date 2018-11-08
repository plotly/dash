# pylint: disable=global-statement
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import os
import pandas as pd
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(sys.argv[0]), os.pardir, os.pardir, os.pardir)
    )
)
module_names = ["dash_table"]
modules = [__import__(module) for module in module_names]
dash_table = modules[0]

url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
df = pd.read_csv(url, nrows=1000)
df = df.values

app = dash.Dash()
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

app.layout = html.Div(
    [
        html.Div(id="derived_virtual_selected_rows_container", children="undefined"),
        html.Div(id="derived_viewport_selected_rows_container", children="undefined"),
        dash_table.DataTable(
            id="table",
            data=df,
            pagination_mode="fe",
            pagination_settings={
                "displayed_pages": 1,
                "current_page": 0,
                "page_size": 250,
            },
            navigation="page",
            columns=[
                {"id": 0, "name": "Complaint ID"},
                {"id": 1, "name": "Product"},
                {"id": 2, "name": "Sub-product"},
                {"id": 3, "name": "Issue"},
                {"id": 4, "name": "Sub-issue"},
                {"id": 5, "name": "State"},
                {"id": 6, "name": "ZIP"},
                {"id": 7, "name": "code"},
                {"id": 8, "name": "Date received"},
                {"id": 9, "name": "Date sent to company"},
                {"id": 10, "name": "Company"},
                {"id": 11, "name": "Company response"},
                {"id": 12, "name": "Timely response?"},
                {"id": 13, "name": "Consumer disputed?"},
            ],
            n_fixed_columns=2,
            n_fixed_rows=1,
            row_selectable=True,
            row_deletable=True,
            sorting="fe",
            filtering=True,
            editable=True,
        ),
    ]
)

@app.callback(
    Output("derived_virtual_selected_rows_container", "children"),
    [Input("table", "derived_virtual_selected_rows")]
)
def exposeDerivedVirtualSelectedRows(rows):
    return str(rows);


@app.callback(
    Output("derived_viewport_selected_rows_container", "children"),
    [Input("table", "derived_viewport_selected_rows")]
)
def exposeDerivedViewportSelectedRows(rows):
    return str(rows);


if __name__ == "__main__":
    app.run_server(port=8083, debug=False)