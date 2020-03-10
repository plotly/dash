import os
from textwrap import dedent
import pandas as pd

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table

ID_PREFIX = "app_data_updating_graph"
IDS = {"table": ID_PREFIX, "container": "{}-container".format(ID_PREFIX)}
_TIMEOUT = 10


def test_rapp002_df_graph(dash_duo):
    df = pd.read_csv(
        os.path.realpath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "assets", "gapminder.csv",
            )
        )
    )

    df = df[df["year"] == 2007]

    app = dash.Dash(
        __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/dZVMbK.css"],
    )
    app.layout = html.Div(
        [
            html.Div(
                dash_table.DataTable(
                    id=IDS["table"],
                    columns=[
                        {"name": i, "id": i, "deletable": True} for i in df.columns
                    ],
                    data=df.to_dict("rows"),
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    row_selectable="multi",
                    row_deletable=True,
                    selected_rows=[],
                    fixed_rows={"headers": True},
                ),
                style={"height": 300, "overflowY": "scroll"},
            ),
            html.Div(id=IDS["container"]),
            dcc.Markdown(
                dedent(
                    """
            ***

            `Table` includes several features for modifying and transforming the
            view of the data. These include:

            - Sorting by column (`sort_action='native'`)
            - Filtering by column (`filter_action='native'`)
            - Editing the cells (`editable=True`)
            - Deleting rows (`row_deletable=True`)
            - Deleting columns (`columns[i].deletable=True`)
            - Selecting rows (`row_selectable='single' | 'multi'`)

            > A quick note on filtering. We have defined our own
            > syntax for performing filtering operations. Here are some
            > examples for this particular dataset:
            > - `lt 50` in the `lifeExp` column
            > - `eq "Canada"` in the `country` column

            By default, these transformations are done clientside.
            Your Dash callbacks can respond to these modifications
            by listening to the `data` property as an `Input`.

            Note that if `data` is an `Input` then the entire
            `data` will be passed over the network: if your data is
            large, then this will become slow. For large data, you have
            two options:
            - Use `data_indices` instead
            - Perform the sorting or filtering in Python instead

            Issues with this example:
            - Row selection callbacks don't work yet: `derived_viewport_indices`
            isn't getting updated on row selection and `selected_rows` doesn't
            track the underlying data (e.g. it will always be [1, 3] even after sorting or filtering)
            """
                )
            ),
            html.Div(id="waitfor"),
        ]
    )

    @app.callback(
        Output(IDS["container"], "children"),
        [
            Input(IDS["table"], "derived_virtual_data"),
            Input(IDS["table"], "selected_rows"),
        ],
    )
    def update_graph(rows, selected_rows):
        # When the table is first rendered, `derived_virtual_data`
        # will be `None`. This is due to an idiosyncracy in Dash
        # (unsupplied properties are always None and Dash calls the dependent
        # callbacks when the component is first rendered).
        # So, if `selected_rows` is `None`, then the component was just rendered
        # and its value will be the same as the component's data.
        # Instead of setting `None` in here, you could also set
        # `derived_virtual_data=df.to_rows('dict')` when you initialize
        # the component.
        if rows is None:
            dff = df
        else:
            dff = pd.DataFrame(rows)

        colors = []
        for i in range(len(dff)):
            if i in selected_rows:
                colors.append("#7FDBFF")
            else:
                colors.append("#0074D9")

        return html.Div(
            [
                dcc.Graph(
                    id=column,
                    figure={
                        "data": [
                            {
                                "x": dff["country"],
                                # check if column exists - user may have deleted it
                                # If `column.deletable=False`, then you don't
                                # need to do this check.
                                "y": dff[column] if column in dff else [],
                                "type": "bar",
                                "marker": {"color": colors},
                            }
                        ],
                        "layout": {
                            "xaxis": {"automargin": True},
                            "yaxis": {"automargin": True},
                            "height": 250,
                            "margin": {"t": 10, "l": 10, "r": 10},
                        },
                    },
                )
                for column in ["pop", "lifeExp", "gdpPercap"]
            ]
        )

    dash_duo.start_server(app)
    dash_duo.wait_for_element("#waitfor")

    dash_duo.wait_for_element("#{}".format(IDS["table"]))

    dash_duo.percy_snapshot("rapp002 - loaded")
