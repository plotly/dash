# pylint: disable=global-statement
import json
import os
import pandas as pd
import sys

import dash
from dash.dependencies import Input, Output
import dash_html_components as html

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(sys.argv[0]),
                     os.pardir, os.pardir, os.pardir)
    )
)
module_names = ["dash_table"]
modules = [__import__(module) for module in module_names]
dash_table = modules[0]

url = ("https://github.com/plotly/datasets/raw/master/"
       "26k-consumer-complaints.csv")
df = pd.read_csv(url, nrows=1000)
# add IDs that don't match but are easily derivable from row #s
data = [
    {k: v for k, v in list(enumerate(row)) + [('id', i + 3000)]}
    for i, row in enumerate(df.values)
]

app = dash.Dash()
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

app.layout = html.Div(
    [
        dash_table.DataTable(
            id="table",
            data=data,
            pagination_mode="fe",
            pagination_settings={
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
        html.Div(id="props_container")
    ]
)

props = [
    'active_cell', 'start_cell', 'end_cell', 'selected_cells',
    'selected_rows', 'selected_row_ids',
    'derived_viewport_selected_rows', 'derived_viewport_selected_row_ids',
    'derived_virtual_selected_rows', 'derived_virtual_selected_row_ids',
    'derived_viewport_indices', 'derived_viewport_row_ids',
    'derived_virtual_indices', 'derived_virtual_row_ids'
]


@app.callback(
    Output("props_container", "children"),
    [Input("table", prop) for prop in props]
)
def show_props(*args):
    return html.Table([
        html.Tr([
            html.Td(prop),
            html.Td(json.dumps(val), id=prop + '_container')
        ])
        for prop, val in zip(props, args)
    ])


if __name__ == "__main__":
    app.run_server(port=8083, debug=False)
