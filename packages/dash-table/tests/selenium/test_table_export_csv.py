import os
import pandas as pd
import dash_table
import dash
import dash.testing.wait as wait


def test_tbex001_table_export(test):
    df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/solar.csv"
    )
    app = dash.Dash(__name__)
    app.layout = dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        export_format="csv",
    )
    test.start_server(app)
    test.wait_for_element(".export", timeout=1).click()

    download = os.path.sep.join((test.download_path, "Data.csv"))
    wait.until(lambda: os.path.exists(download), timeout=2)

    df_bis = pd.read_csv(download)
    assert df_bis.equals(df)
    assert test.get_log_errors() == []
