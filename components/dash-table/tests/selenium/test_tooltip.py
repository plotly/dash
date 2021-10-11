import dash
import math
import pytest
import time
import dash.testing.wait as wait
from dash.dash_table import DataTable

columns = [dict(id=str(i), name="Column {}".format(i)) for i in range(1, 30)]

data = []
for i in range(1, 100):
    datum = dict()
    data.append(datum)
    for j in columns:
        datum[j["id"]] = "{}-{}".format(i, j["id"])

tooltip_data_text = []
for i in range(1, 100):
    datum = dict()
    tooltip_data_text.append(datum)
    for j in columns:
        datum[j["id"]] = dict(type="text", value=";; {}-{}".format(i, j["id"]))

tooltip_data_markdown = []
for i in range(1, 100):
    datum = dict()
    tooltip_data_markdown.append(datum)
    for j in columns:
        datum[j["id"]] = dict(type="markdown", value="### ;; {}-{}".format(i, j["id"]))

base_props = dict(
    id="table", columns=columns, data=data, tooltip_delay=None, tooltip_duration=None
)


def assert_aligned(cell, tooltip):
    assert tooltip.location["x"] <= (cell.location["x"] + cell.size["width"])
    assert (tooltip.location["x"] + tooltip.size["width"]) >= cell.location["x"]


@pytest.mark.parametrize(
    "fixed_rows",
    [
        dict(),
        dict(fixed_rows=dict(headers=True)),
        dict(fixed_rows=dict(headers=True, data=1)),
    ],
)
@pytest.mark.parametrize(
    "fixed_columns",
    [
        dict(),
        dict(fixed_columns=dict(headers=True)),
        dict(fixed_columns=dict(headers=True, data=1)),
    ],
)
@pytest.mark.parametrize(
    "ops", [dict(), dict(row_selectable="single", row_deletable=True)]
)
def test_ttip001_displays_aligned_tooltip(test, fixed_rows, fixed_columns, ops):
    props = {
        **base_props,
        **fixed_rows,
        **fixed_columns,
        **ops,
        **dict(tooltip_data=tooltip_data_text),
    }

    app = dash.Dash(__name__)
    app.layout = DataTable(**props)

    test.start_server(app)

    target = test.table("table")

    cell = target.cell(0, 0)
    tooltip = target.tooltip

    target.is_ready()
    cell.move_to()
    assert tooltip.exists()
    assert tooltip.get_text() == ";; 1-1"
    assert_aligned(cell.get(), tooltip.get())

    mid = math.ceil(len(columns) / 2)
    cell = target.cell(0, mid)
    cell.move_to()
    assert_aligned(cell.get(), tooltip.get())

    cell = target.cell(0, len(columns) - 1)
    cell.move_to()
    assert_aligned(cell.get(), tooltip.get())
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "tooltip_data,expected_text",
    [
        (dict(tooltip_data=tooltip_data_text), ";; 1-1"),
        (dict(tooltip_data=tooltip_data_markdown), "<h3>;; 1-1</h3>"),
    ],
)
def test_ttip002_displays_tooltip_content(test, tooltip_data, expected_text):
    props = {**base_props, **tooltip_data}

    app = dash.Dash(__name__)
    app.layout = DataTable(**props)

    test.start_server(app)

    target = test.table("table")

    cell = target.cell(0, 0)
    tooltip = target.tooltip

    target.is_ready()

    cell.move_to()
    assert tooltip.exists()
    assert tooltip.get_text().strip() == expected_text
    assert test.get_log_errors() == []


def test_ttip003_tooltip_disappears(test):
    props = {
        **base_props,
        **dict(
            tooltip_delay=2000, tooltip_duration=2000, tooltip_data=tooltip_data_text
        ),
    }

    app = dash.Dash(__name__)
    app.layout = DataTable(**props)

    test.start_server(app)

    target = test.table("table")
    tooltip = target.tooltip

    target.is_ready()

    target.cell(0, 0).move_to()
    assert not tooltip.exists()

    wait.until(lambda: tooltip.exists(), 2.5)
    wait.until(lambda: not tooltip.exists(), 2.5)
    assert test.get_log_errors() == []


ttip004_tooltip = {
    "1": "text1",
    "2": {"use_with": "data", "value": "text2"},
    "3": {"use_with": "header", "value": "text3"},
}


@pytest.mark.parametrize(
    "tooltip_data,tooltip_header,data_expected,header_expected",
    [
        (
            [{"1": "alt-text1"}],
            {"1": ["alt-header1-row1", "alt-header1-row2"]},
            ["alt-text1", "text1"],
            ["alt-header1-row1", "alt-header1-row2"],
        ),
        (
            [{"1": "alt-text1"}],
            {"1": [None, "alt-header1-row1"]},
            ["alt-text1", "text1"],
            ["text1", "alt-header1-row1"],
        ),
        (
            [{"1": "alt-text1"}, {"1": "alt-text2"}],
            {"1": "alt-header1-row1"},
            ["alt-text1", "alt-text2"],
            ["alt-header1-row1", "alt-header1-row1"],
        ),
    ],
)
def test_ttip004_tooltip_applied(
    test, tooltip_data, tooltip_header, data_expected, header_expected
):
    props = {
        **base_props,
        "columns": [
            dict(
                id=str(i),
                name=["Column {}".format(math.ceil(i / 3)), "Column {}".format(i)],
            )
            for i in range(1, 30)
        ],
        "merge_duplicate_headers": True,
        "tooltip_delay": 0,
        "tooltip_duration": 5000,
        "tooltip": {
            "1": "text1",
            "2": {"use_with": "data", "value": "text2"},
            "3": {"use_with": "header", "value": "text3"},
        },
        "tooltip_data": tooltip_data,
        "tooltip_header": tooltip_header,
    }

    app = dash.Dash(__name__)
    app.layout = DataTable(**props)

    test.start_server(app)

    target = test.table("table")
    target.is_ready()

    cell55 = target.cell(5, "5")
    tooltip = target.tooltip

    target.cell(0, "1").move_to()
    wait.until(lambda: target.tooltip.exists(), 3)
    assert tooltip.get_text().strip() == data_expected[0]
    cell55.move_to()

    target.cell(1, "1").move_to()
    wait.until(lambda: target.tooltip.exists(), 3)
    assert tooltip.get_text().strip() == data_expected[1]
    cell55.move_to()

    target.cell(0, "2").move_to()
    wait.until(lambda: target.tooltip.exists(), 3)
    assert tooltip.get_text().strip() == "text2"
    cell55.move_to()

    target.cell(0, "3").move_to()
    time.sleep(1)
    wait.until(lambda: target.tooltip.missing(), 3)
    cell55.move_to()

    target.column("1").move_to(0)
    wait.until(lambda: target.tooltip.exists(), 3)
    assert tooltip.get_text().strip() == header_expected[0]
    cell55.move_to()

    target.column("1").move_to(1)
    wait.until(lambda: target.tooltip.exists(), 3)
    assert tooltip.get_text().strip() == header_expected[1]
    cell55.move_to()

    target.column("2").move_to(1)
    time.sleep(1)
    wait.until(lambda: target.tooltip.missing(), 3)
    cell55.move_to()

    target.column("3").move_to(1)
    wait.until(lambda: target.tooltip.exists(), 3)
    assert tooltip.get_text().strip() == "text3"
    cell55.move_to()

    assert test.get_log_errors() == []
