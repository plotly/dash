# pylint: disable=global-statement
import dash
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
modules = [__import__(x) for x in module_names]
dash_table = modules[0]

url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
df = pd.read_csv(url)

df['Complaint ID'] = df['Complaint ID'].map(lambda x: '**' + str(x) + '**')
df['Product'] = df['Product'].map(lambda x: '[' + str(x) + '](plot.ly)')
df['Issue'] = df['Issue'].map(lambda x: '![' + str(x) + '](https://dash.plot.ly/assets/images/logo.png)')
df['State'] = df['State'].map(lambda x: '```python\n"{}"\n```'.format(x))

df = df.values

app = dash.Dash()

app.layout = html.Div(
    [
        html.Div(id="container", children="Hello World"),
        dash_table.DataTable(
            id="table",
            data=df[0:250],
            columns=[
                {"id": 1, "name": "Complaint ID", "presentation": "markdown"},
                {"id": 2, "name": "Product", "presentation": "markdown"},
                {"id": 3, "name": "Sub-product"},
                {"id": 4, "name": "Issue", "presentation": "markdown"},
                {"id": 5, "name": "Sub-issue"},
                {"id": 6, "name": "State", "presentation": "markdown"},
                {"id": 7, "name": "ZIP"}
            ],
            editable=True,
            sort_action='native',
            include_headers_on_copy_paste=True
        )
    ]
)

app.run_server(debug=False, port=8087)
