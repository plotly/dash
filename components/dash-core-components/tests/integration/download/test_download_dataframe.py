import os
from dash import Dash, Input, Output, dcc, html

import pytest
import pandas as pd
import numpy as np

from dash.testing.wait import until


@pytest.mark.parametrize(
    "fmt", ("csv", "json", "html", "feather", "parquet", "stata", "pickle")
)
def test_dldf001_download_dataframe(fmt, dash_dcc):
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})
    reader = getattr(pd, f"read_{fmt}")  # e.g. read_csv
    writer = getattr(df, f"to_{fmt}")  # e.g. to_csv
    filename = f"df.{fmt}"
    # Create app.
    app = Dash(__name__, prevent_initial_callbacks=True)
    app.layout = html.Div(
        [html.Button("Click me", id="btn"), dcc.Download(id="download")]
    )

    @app.callback(Output("download", "data"), Input("btn", "n_clicks"))
    def download(_):
        # For csv and html, the index must be removed to preserve the structure.
        if fmt in ["csv", "html", "excel"]:
            return dcc.send_data_frame(writer, filename, index=False)
        # For csv and html, the index must be removed to preserve the structure.
        if fmt in ["stata"]:
            a = dcc.send_data_frame(writer, filename, write_index=False)
            return a
        # For other formats, no modifications are needed.
        return dcc.send_data_frame(writer, filename)

    dash_dcc.start_server(app)

    # Check that there is nothing before clicking
    fp = os.path.join(dash_dcc.download_path, filename)
    assert not os.path.isfile(fp)

    dash_dcc.find_element("#btn").click()

    # Check that a file has been download, and that it's content matches the original data frame.
    until(lambda: os.path.exists(fp), 10)
    df_download = reader(fp)
    if isinstance(df_download, list):
        df_download = df_download[0]
    # For stata data, pandas equals fails. Hence, a custom equals is used instead.
    assert df.columns.equals(df_download.columns)
    assert df.index.equals(df_download.index)
    np.testing.assert_array_equal(df.values, df_download.values)

    assert dash_dcc.get_logs() == []
