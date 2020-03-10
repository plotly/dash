import os
from textwrap import dedent
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table


ID_PREFIX = "app_data_updating_graph_be"
IDS = {
    "table": ID_PREFIX,
    "container": "{}-container".format(ID_PREFIX),
    "table-sorting": "{}-sorting".format(ID_PREFIX),
    "table-multi-sorting": "{}-multi-sorting".format(ID_PREFIX),
    "table-filtering": "{}-filtering".format(ID_PREFIX),
    "table-sorting-filtering": "{}-sorting-filtering".format(ID_PREFIX),
    "table-paging-selection": "{}-paging-selection".format(ID_PREFIX),
    "table-paging-with-graph": "{}-table-paging-with-graph".format(ID_PREFIX),
    "table-paging-with-graph-container": "{}-table-paging-with-graph-container".format(
        ID_PREFIX
    ),
}
PAGE_SIZE = 5


def test_rapp001_df_backend_paging(dash_duo):
    df = pd.read_csv(
        os.path.realpath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "assets", "gapminder.csv",
            )
        )
    )
    df = df[df["year"] == 2007]
    df["index"] = range(1, len(df) + 1)

    app = dash.Dash(
        __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/dZVMbK.css"],
    )
    app.config.suppress_callback_exceptions = True

    def section_title(title):
        return html.H4(title, style={"marginTop": "20px"})

    app.layout = html.Div(
        [
            section_title("Backend Paging"),
            dash_table.DataTable(
                id=IDS["table"],
                columns=[
                    {"name": i, "id": i, "deletable": True} for i in sorted(df.columns)
                ],
                page_current=0,
                page_size=PAGE_SIZE,
                page_action="custom",
            ),
            html.Hr(),
            dcc.Markdown(
                dedent(
                    """
            With backend paging, we can have front-end sorting and filtering
            but it will only filter and sort the data that exists on the page.

            This should be avoided. Your users will expect
            that sorting and filtering is happening on the entire dataset and,
            with large pages, might not be aware that this is only occuring
            on the current page.

            Instead, we recommend implementing sorting and filtering on the
            backend as well. That is, on the entire underlying dataset.
            """
                )
            ),
            section_title("Backend Paging with Sorting"),
            dash_table.DataTable(
                id=IDS["table-sorting"],
                columns=[
                    {"name": i, "id": i, "deletable": True} for i in sorted(df.columns)
                ],
                page_current=0,
                page_size=PAGE_SIZE,
                page_action="custom",
                sort_action="custom",
                sort_mode="single",
                sort_by=[],
            ),
            section_title("Backend Paging with Multi Column Sorting"),
            dcc.Markdown(
                dedent(
                    """
            Multi-column sort allows you to sort by multiple columns.
            This is useful when you have categorical columns with repeated
            values and you're interested in seeing the sorted values for
            each category.

            In this example, try sorting by continent and then any other column.
            """
                )
            ),
            dash_table.DataTable(
                id=IDS["table-multi-sorting"],
                columns=[
                    {"name": i, "id": i, "deletable": True} for i in sorted(df.columns)
                ],
                page_current=0,
                page_size=PAGE_SIZE,
                page_action="custom",
                sort_action="custom",
                sort_mode="multi",
                sort_by=[],
            ),
            section_title("Backend Paging with Filtering"),
            dcc.Markdown(
                dedent(
                    """
            Dash Table's front-end filtering has its own filtering expression
            language.

            Currently, backend filtering must parse the same filtering language.
            If you write an expression that is not "valid" under the filtering
            language, then it will not be passed to the backend.

            This limitation will be removed in the future to allow you to
            write your own expression query language.

            In this example, we've written a Pandas backend for the filtering
            language. It supports `eq`, `<`, and `>`. For example, try:

            - Enter `eq Asia` in the "continent" column
            - Enter `> 5000` in the "gdpPercap" column
            - Enter `< 80` in the `lifeExp` column

            """
                )
            ),
            dash_table.DataTable(
                id=IDS["table-filtering"],
                columns=[
                    {"name": i, "id": i, "deletable": True} for i in sorted(df.columns)
                ],
                page_current=0,
                page_size=PAGE_SIZE,
                page_action="custom",
                filter_action="custom",
                filter_query="",
            ),
            section_title("Backend Paging with Filtering and Multi-Column Sorting"),
            dash_table.DataTable(
                id=IDS["table-sorting-filtering"],
                columns=[
                    {"name": i, "id": i, "deletable": True} for i in sorted(df.columns)
                ],
                page_current=0,
                page_size=PAGE_SIZE,
                page_action="custom",
                filter_action="custom",
                filter_query="",
                sort_action="custom",
                sort_mode="multi",
                sort_by=[],
            ),
            section_title("Connecting Backend Paging with a Graph"),
            dcc.Markdown(
                dedent(
                    """
            This final example ties it all together: the graph component
            displays the current page of the `data`.
            """
                )
            ),
            html.Div(
                className="row",
                children=[
                    html.Div(
                        dash_table.DataTable(
                            id=IDS["table-paging-with-graph"],
                            columns=[
                                {"name": i, "id": i, "deletable": True}
                                for i in sorted(df.columns)
                            ],
                            page_current=0,
                            page_size=20,
                            page_action="custom",
                            filter_action="custom",
                            filter_query="",
                            sort_action="custom",
                            sort_mode="multi",
                            sort_by=[],
                        ),
                        style={"height": 750, "overflowY": "scroll"},
                        className="six columns",
                    ),
                    html.Div(
                        id=IDS["table-paging-with-graph-container"],
                        className="six columns",
                    ),
                ],
            ),
            html.Div(id="waitfor"),
        ]
    )

    @app.callback(
        Output(IDS["table"], "data"),
        [Input(IDS["table"], "page_current"), Input(IDS["table"], "page_size")],
    )
    def update_data(page_current, page_size):
        return df.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("rows")

    @app.callback(
        Output(IDS["table-sorting"], "data"),
        [
            Input(IDS["table-sorting"], "page_current"),
            Input(IDS["table-sorting"], "page_size"),
            Input(IDS["table-sorting"], "sort_by"),
        ],
    )
    def update_graph(page_current, page_size, sort_by):
        # print(sort_by)
        if len(sort_by):
            dff = df.sort_values(
                sort_by[0]["columnId"],
                ascending=sort_by[0]["direction"] == "asc",
                inplace=False,
            )
        else:
            # No sort is applied
            dff = df

        return dff.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("rows")

    @app.callback(
        Output(IDS["table-multi-sorting"], "data"),
        [
            Input(IDS["table-multi-sorting"], "page_current"),
            Input(IDS["table-multi-sorting"], "page_size"),
            Input(IDS["table-multi-sorting"], "sort_by"),
        ],
    )
    def update_multi_data(page_current, page_size, sort_by):
        # print(sort_by)
        if len(sort_by):
            dff = df.sort_values(
                [col["columnId"] for col in sort_by],
                ascending=[col["direction"] == "asc" for col in sort_by],
                inplace=False,
            )
        else:
            # No sort is applied
            dff = df

        return dff.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("rows")

    @app.callback(
        Output(IDS["table-filtering"], "data"),
        [
            Input(IDS["table-filtering"], "page_current"),
            Input(IDS["table-filtering"], "page_size"),
            Input(IDS["table-filtering"], "filter_query"),
        ],
    )
    def updat_filtering_data(page_current, page_size, filter_query):
        # print(filter_query)
        filtering_expressions = filter_query.split(" && ")
        dff = df
        for filter_query in filtering_expressions:
            if " eq " in filter_query:
                col_name = filter_query.split(" eq ")[0]
                filter_value = filter_query.split(" eq ")[1]
                dff = dff.loc[dff[col_name] == filter_value]
            if " > " in filter_query:
                col_name = filter_query.split(" > ")[0]
                filter_value = float(filter_query.split(" > ")[1])
                dff = dff.loc[dff[col_name] > filter_value]
            if " < " in filter_query:
                col_name = filter_query.split(" < ")[0]
                filter_value = float(filter_query.split(" < ")[1])
                dff = dff.loc[dff[col_name] < filter_value]

        return dff.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("rows")

    @app.callback(
        Output(IDS["table-sorting-filtering"], "data"),
        [
            Input(IDS["table-sorting-filtering"], "page_current"),
            Input(IDS["table-sorting-filtering"], "page_size"),
            Input(IDS["table-sorting-filtering"], "sort_by"),
            Input(IDS["table-sorting-filtering"], "filter_query"),
        ],
    )
    def update_sorting_filtering_data(page_current, page_size, sort_by, filter_query):
        filtering_expressions = filter_query.split(" && ")
        dff = df
        for filter_query in filtering_expressions:
            if " eq " in filter_query:
                col_name = filter_query.split(" eq ")[0]
                filter_value = filter_query.split(" eq ")[1]
                dff = dff.loc[dff[col_name] == filter_value]
            if " > " in filter_query:
                col_name = filter_query.split(" > ")[0]
                filter_value = float(filter_query.split(" > ")[1])
                dff = dff.loc[dff[col_name] > filter_value]
            if " < " in filter_query:
                col_name = filter_query.split(" < ")[0]
                filter_value = float(filter_query.split(" < ")[1])
                dff = dff.loc[dff[col_name] < filter_value]

        if len(sort_by):
            dff = dff.sort_values(
                [col["columnId"] for col in sort_by],
                ascending=[col["direction"] == "asc" for col in sort_by],
                inplace=False,
            )

        return dff.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("rows")

    @app.callback(
        Output(IDS["table-paging-with-graph"], "data"),
        [
            Input(IDS["table-paging-with-graph"], "page_current"),
            Input(IDS["table-paging-with-graph"], "page_size"),
            Input(IDS["table-paging-with-graph"], "sort_by"),
            Input(IDS["table-paging-with-graph"], "filter_query"),
        ],
    )
    def update_table(page_current, page_size, sort_by, filter_query):
        filtering_expressions = filter_query.split(" && ")
        dff = df
        for filter_query in filtering_expressions:
            if " eq " in filter_query:
                col_name = filter_query.split(" eq ")[0]
                filter_value = filter_query.split(" eq ")[1]
                dff = dff.loc[dff[col_name] == filter_value]
            if " > " in filter_query:
                col_name = filter_query.split(" > ")[0]
                filter_value = float(filter_query.split(" > ")[1])
                dff = dff.loc[dff[col_name] > filter_value]
            if " < " in filter_query:
                col_name = filter_query.split(" < ")[0]
                filter_value = float(filter_query.split(" < ")[1])
                dff = dff.loc[dff[col_name] < filter_value]

        if len(sort_by):
            dff = dff.sort_values(
                [col["columnId"] for col in sort_by],
                ascending=[col["direction"] == "asc" for col in sort_by],
                inplace=False,
            )

        return dff.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("rows")

    @app.callback(
        Output(IDS["table-paging-with-graph-container"], "children"),
        [Input(IDS["table-paging-with-graph"], "data")],
    )
    def update_children(rows):
        dff = pd.DataFrame(rows)
        return html.Div(
            [
                dcc.Graph(
                    id=column,
                    figure={
                        "data": [
                            {
                                "x": dff["country"],
                                "y": dff[column] if column in dff else [],
                                "type": "bar",
                                "marker": {"color": "#0074D9"},
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
    dash_duo.percy_snapshot("rapp001 - loaded")
