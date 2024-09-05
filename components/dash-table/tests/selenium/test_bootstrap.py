# import dash
# import pytest

# import dash_bootstrap_components as dbc
# from dash import html
# from dash.dash_table import DataTable

# import pandas as pd

# url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
# rawDf = pd.read_csv(url)
# df = rawDf.to_dict("records")


# def get_app(fixed_rows, fixed_columns, ops):
#     app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#     props = dict(
#         id="table",
#         data=df[0:250],
#         columns=[
#             {"name": i, "id": i, "hideable": i == "Complaint ID"} for i in rawDf.columns
#         ],
#         style_table=dict(height="500px", maxHeight="500px", overflow="auto"),
#         editable=True,
#         sort_action="native",
#         include_headers_on_copy_paste=True,
#         **fixed_rows,
#         **fixed_columns,
#         **ops
#     )

#     app.layout = html.Div([DataTable(**props)])

#     return app


# @pytest.mark.parametrize(
#     "fixed_rows,fixed_rows_description",
#     [(dict(), "unfixed_rows"), (dict(fixed_rows=dict(headers=True)), "fixed_rows")],
# )
# @pytest.mark.parametrize(
#     "fixed_columns,fixed_columns_description",
#     [
#         (dict(), "unfixed_columns"),
#         (dict(fixed_columns=dict(headers=True)), "fixed_columns"),
#     ],
# )
# @pytest.mark.parametrize(
#     "ops,ops_description",
#     [
#         (dict(), "ops: none"),
#         (dict(row_selectable="single", row_deletable=True), "ops: sinle+deletable"),
#         (dict(row_selectable="multi", row_deletable=True), "ops: multi+deletable"),
#     ],
# )
# @pytest.mark.skip(reason="Requires updates to `dash-bootstrap-components` imports")
# def test_tbbs001_display(
#     dash_thread_server,
#     dash_duo,
#     test,
#     fixed_rows,
#     fixed_columns,
#     ops,
#     fixed_rows_description,
#     fixed_columns_description,
#     ops_description,
# ):
#     test.start_server(get_app(fixed_rows, fixed_columns, ops))

#     test.table("table").is_ready()

#     test.percy_snapshot(
#         "DataTable Bootstrap side-effects with rows={} columns={} ops={}".format(
#             fixed_rows_description, fixed_columns_description, ops_description
#         )
#     )
