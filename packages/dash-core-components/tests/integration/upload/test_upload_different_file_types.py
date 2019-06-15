import io
import base64
import os
import time
import pytest
import pandas as pd

import dash
from dash.dependencies import Input, Output

import dash_core_components as dcc
import dash_html_components as html
from dash_table import DataTable


pre_style = {"whiteSpace": "pre-wrap", "wordBreak": "break-all"}


def load_table(filetype, payload):
    df = (
        pd.read_csv(io.StringIO(base64.b64decode(payload).decode("utf-8")))
        if filetype == "csv"
        else pd.read_excel(io.BytesIO(base64.b64decode(payload)))
    )

    return html.Div(
        [
            DataTable(
                data=df.to_dict("records"),
                columns=[{"id": i} for i in ["city", "country"]],
            ),
            html.Hr(),
            html.Div("Raw Content"),
            html.Pre(payload, style=pre_style),
        ]
    )


def load_data_by_type(filetype, contents):
    children = []
    _type, payload = contents.split(",")
    if filetype in {"csv", "xlsx", "xls"}:
        return load_table(filetype, payload)
    elif filetype in {"png", "svg"}:
        children = [html.Img(src=contents)]

    children.extend(
        (html.Hr(), html.Div("Raw Content"), html.Pre(payload, style=pre_style))
    )
    return html.Div(children)


@pytest.mark.parametrize("filetype", ("csv", "xlsx", "xls", "png", "svg"))
def test_upft001_test_upload_with_different_file_types(filetype, dash_duo):

    filepath = os.path.join(
        os.path.dirname(__file__),
        "upload-assets",
        "upft001.{}".format(filetype),
    )

    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Div(filepath, id="waitfor"),
            html.Div(
                id="upload-div",
                children=dcc.Upload(
                    id="upload",
                    children=html.Div(
                        ["Drag and Drop or ", html.A("Select a File")]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                    },
                ),
            ),
            html.Div(id="output"),
            html.Div(DataTable(data=[{}]), style={"display": "none"}),
        ]
    )

    @app.callback(Output("output", "children"), [Input("upload", "contents")])
    def update_output(contents):
        if contents is not None:
            return load_data_by_type(filetype, contents)

    dash_duo.start_server(app)

    upload_div = dash_duo.wait_for_element("#upload-div input[type=file]")
    upload_div.send_keys(filepath)
    time.sleep(0.5)
    dash_duo.percy_snapshot(filepath)
