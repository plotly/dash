import os
import pandas as pd
import dash_table
import dash
import dash.testing.wait as wait


def test_tbex001_table_export(dash_duo):
    df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/solar.csv"
    )
    app = dash.Dash(__name__)
    app.layout = dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        export_format="xlsx",
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_element(".export").click()

    download = os.path.sep.join((dash_duo.download_path, "Data.xlsx"))
    wait.until(lambda: os.path.exists(download), timeout=2)

    df_bis = pd.read_excel(download)
    assert df_bis.equals(df)
