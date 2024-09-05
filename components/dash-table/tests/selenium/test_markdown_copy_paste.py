import pytest

import dash
from dash.testing import wait
from dash.dash_table import DataTable

import pandas as pd

url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
rawDf = pd.read_csv(url)
rawDf["Complaint ID"] = rawDf["Complaint ID"].map(lambda x: "**" + str(x) + "**")
rawDf["Product"] = rawDf["Product"].map(lambda x: "[" + str(x) + "](plot.ly)")
rawDf["Issue"] = rawDf["Issue"].map(lambda x: "![" + str(x) + "](assets/logo.png)")
rawDf["State"] = rawDf["State"].map(lambda x: '```python\n"{}"\n```'.format(x))

df = rawDf.to_dict("records")


def get_app():
    app = dash.Dash(__name__)

    app.layout = DataTable(
        id="table",
        data=df[0:250],
        columns=[
            {"id": "Complaint ID", "name": "Complaint ID", "presentation": "markdown"},
            {"id": "Product", "name": "Product", "presentation": "markdown"},
            {"id": "Sub-product", "name": "Sub-product"},
            {"id": "Issue", "name": "Issue", "presentation": "markdown"},
            {"id": "Sub-issue", "name": "Sub-issue"},
            {"id": "State", "name": "State", "presentation": "markdown"},
            {"id": "ZIP", "name": "ZIP"},
        ],
        editable=True,
        sort_action="native",
        include_headers_on_copy_paste=True,
    )

    return app


@pytest.mark.skip(
    reason="Prop `data_previous` is not correctly updated with copy+paste"
)
def test_tmcp001_copy_markdown_to_text(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(0, "Issue").click()

    test.copy()
    target.cell(0, "Sub-product").click()
    test.paste()

    wait.until(lambda: target.cell(0, 2).get_text() == df[0].get("Issue"), 3)
    assert test.get_log_errors() == []


@pytest.mark.skip(
    reason="Prop `data_previous` is not correctly updated with copy+paste"
)
def test_tmcp002_copy_markdown_to_markdown(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(0, "Product").click()

    test.copy()
    target.cell(0, "Complaint ID").click()
    test.paste()

    wait.until(
        lambda: target.cell(0, "Complaint ID").get_text()
        == target.cell(0, "Product").get_text(),
        3,
    )
    assert test.get_log_errors() == []


@pytest.mark.skip(
    reason="Prop `data_previous` is not correctly updated with copy+paste"
)
def test_tmcp003_copy_text_to_markdown(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(1, "Sub-product").click()

    test.copy()
    target.cell(1, "Product").click()
    test.paste()

    wait.until(
        lambda: target.cell(1, "Product")
        .find_inside(".dash-cell-value > p")
        .get_attribute("innerHTML")
        == df[1].get("Sub-product"),
        3,
    )
    assert test.get_log_errors() == []


def test_tmcp004_copy_null_text_to_markdown(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(0, "Sub-product").click()

    test.copy()
    target.cell(0, "Product").click()
    test.paste()

    wait.until(
        lambda: target.cell(0, "Product")
        .find_inside(".dash-cell-value > p")
        .get_attribute("innerHTML")
        == "null",
        3,
    )
    assert test.get_log_errors() == []
