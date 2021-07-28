import os
import pandas as pd
import pytest
import dash.dash_table as dash_table
import dash
import dash.testing.wait as wait


@pytest.mark.parametrize(
    "format,reader", [("csv", pd.read_csv), ("xlsx", pd.read_excel)]
)
def test_tbex001_table_export_csv(test, format, reader):
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "assets/solar.csv"))
    app = dash.Dash(__name__)
    app.layout = dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        export_format=format,
    )
    test.start_server(app)
    test.wait_for_element(".export", timeout=1).click()

    download = os.path.join(test.download_path, "Data." + format)
    wait.until(lambda: os.path.exists(download), timeout=3)

    df_bis = reader(download)
    assert df_bis.equals(df)
    assert test.get_log_errors() == []
