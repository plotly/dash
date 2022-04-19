import dash

from utils import read_write_modes

from dash.dash_table import DataTable

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd
import pytest

url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
rawDf = pd.read_csv(url)
df = rawDf.to_dict("records")


def get_app(props=dict()):
    app = dash.Dash(__name__)

    baseProps = dict(
        id="table",
        columns=[{"name": i, "id": i} for i in rawDf.columns],
        data=df,
        editable=True,
        filter_action="native",
        fixed_columns={"headers": True},
        fixed_rows={"headers": True},
        page_action="native",
        row_deletable=True,
        row_selectable=True,
        sort_action="native",
    )

    baseProps.update(props)

    app.layout = DataTable(**baseProps)

    return app


@pytest.mark.parametrize("props", read_write_modes)
def test_tbst001_get_cell(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    assert target.cell(0, 0).get_text() == "0"
    target.paging.next.click()
    assert target.cell(0, 0).get_text() == "250"
    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", read_write_modes)
def test_tbst002_select_all_text(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.cell(0, 1).click()

    assert target.cell(0, 1).get_text() == test.get_selected_text()
    assert test.get_log_errors() == []


# https://github.com/plotly/dash-table/issues/50
@pytest.mark.parametrize("props", [dict(editable=False), dict(editable=True)])
def test_tbst003_edit_on_enter(test, props):
    test.start_server(get_app(props))

    target = test.table("table")
    initial_text = target.cell(249, 0).get_text()

    target.cell(249, 0).click()
    test.send_keys("abc" + Keys.ENTER)

    if props.get("editable"):
        assert target.cell(249, 0).get_text() == "abc"
    else:
        assert target.cell(249, 0).get_text() == initial_text

    assert test.get_log_errors() == []


# https://github.com/plotly/dash-table/issues/107
@pytest.mark.parametrize("props", [dict(editable=False), dict(editable=True)])
def test_tbst004_edit_on_tab(test, props):
    test.start_server(get_app(props))

    target = test.table("table")
    initial_text = target.cell(249, 0).get_text()

    target.cell(249, 0).click()
    test.send_keys("abc" + Keys.TAB)

    if props.get("editable"):
        assert target.cell(249, 0).get_text() == "abc"
    else:
        assert target.cell(249, 0).get_text() == initial_text

    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", [dict(editable=False), dict(editable=True)])
def test_tbst005_edit_last_row_on_click_outside(test, props):
    test.start_server(get_app(props))

    target = test.table("table")
    initial_text = target.cell(249, 0).get_text()

    target.cell(249, 0).click()
    test.send_keys("abc")
    target.cell(248, 0).click()

    if props.get("editable"):
        assert target.cell(249, 0).get_text() == "abc"
    else:
        assert target.cell(249, 0).get_text() == initial_text

    assert test.get_log_errors() == []


# https://github.com/plotly/dash-table/issues/141
def test_tbst006_focused_arrow_left(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(249, 1).click()
    test.send_keys("abc" + Keys.LEFT)

    assert target.cell(249, 1).get_text() == "abc"
    assert target.cell(249, 0).is_focused()
    assert test.get_log_errors() == []


# https://github.com/plotly/dash-table/issues/141
def test_tbst007_active_focused_arrow_right(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(249, 0).click()
    test.send_keys("abc" + Keys.RIGHT)

    assert target.cell(249, 0).get_text() == "abc"
    assert target.cell(249, 1).is_focused()
    assert test.get_log_errors() == []


# https://github.com/plotly/dash-table/issues/141
def test_tbst008_active_focused_arrow_up(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(249, 0).click()
    test.send_keys("abc" + Keys.UP)

    assert target.cell(249, 0).get_text() == "abc"
    assert target.cell(248, 0).is_focused()
    assert test.get_log_errors() == []


# https://github.com/plotly/dash-table/issues/141
def test_tbst009_active_focused_arrow_down(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(249, 0).click()
    test.send_keys("abc" + Keys.DOWN)

    assert target.cell(249, 0).get_text() == "abc"
    assert target.cell(249, 0).is_focused()
    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", read_write_modes)
def test_tbst010_active_with_dblclick(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.cell(0, 0).double_click()
    assert target.cell(0, 0).is_active()
    assert target.cell(0, 0).get_text() == test.get_selected_text()
    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", read_write_modes)
def test_tbst011_delete_row(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    text01 = target.cell(1, 0).get_text()
    target.row(0).delete()

    assert target.cell(0, 0).get_text() == text01
    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", read_write_modes)
def test_tbst012_delete_sorted_row(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.column(rawDf.columns[0]).sort()  # None -> ASC
    target.column(rawDf.columns[0]).sort()  # ASC -> DESC

    text01 = target.cell(1, 0).get_text()
    target.row(0).delete()

    assert target.cell(0, 0).get_text() == text01
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "props",
    read_write_modes
    + [
        dict(editable=False, row_deletable=False),
    ],
)
def test_tbst013_select_row(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.row(0).select()

    assert target.row(0).is_selected()
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "props",
    read_write_modes
    + [
        dict(editable=False, row_deletable=False),
    ],
)
def test_tbst014_selected_sorted_row(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.column(rawDf.columns[0]).sort()  # None -> ASC
    target.column(rawDf.columns[0]).sort()  # ASC -> DESC
    target.row(0).select()

    assert target.row(0).is_selected()
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "props",
    read_write_modes
    + [
        dict(editable=False, row_deletable=False),
    ],
)
def test_tbst015_selected_row_respects_sort(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.row(0).select()

    assert target.row(0).is_selected()

    target.column(rawDf.columns[0]).sort()  # None -> ASC
    target.column(rawDf.columns[0]).sort()  # ASC -> DESC

    assert not target.row(0).is_selected()

    target.column(rawDf.columns[0]).sort()  # DESC -> None

    assert target.row(0).is_selected()
    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", read_write_modes)
def test_tbst016_delete_cell(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.cell(0, 1).click()
    test.send_keys(Keys.BACKSPACE)
    test.send_keys(Keys.ENTER)

    assert target.cell(0, 1).get_text() == ""
    assert test.get_log_errors() == []


@pytest.mark.skip(reason="https://github.com/plotly/dash-table/issues/700")
@pytest.mark.parametrize("props", read_write_modes)
def test_tbst017_delete_cell_updates_while_selected(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.cell(0, 1).click()
    test.send_keys(Keys.BACKSPACE)

    assert target.cell(0, 1).get_text() == ""
    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", read_write_modes)
def test_tbst018_delete_multiple_cells(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.cell(0, 1).click()
    with test.hold(Keys.SHIFT):
        ActionChains(test.driver).send_keys(Keys.DOWN).send_keys(Keys.RIGHT).perform()

    ActionChains(test.driver).send_keys(Keys.BACKSPACE).send_keys(Keys.ENTER).perform()

    for row in range(2):
        for col in range(1, 3):
            assert target.cell(row, col).get_text() == ""

    assert test.get_log_errors() == []


@pytest.mark.skip(reason="https://github.com/plotly/dash-table/issues/700")
@pytest.mark.parametrize("props", read_write_modes)
def test_tbst019_delete_multiple_cells_while_selected(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.cell(0, 1).click()
    with test.hold(Keys.SHIFT):
        ActionChains(test.driver).send_keys(Keys.DOWN).send_keys(Keys.RIGHT).perform()

    ActionChains(test.driver).send_keys(Keys.BACKSPACE).perform()

    for row in range(2):
        for col in range(1, 3):
            assert target.cell(row, col).get_text() == ""

    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", read_write_modes)
def test_tbst020_sorted_table_delete_cell(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.column(rawDf.columns[0]).sort()  # None -> ASC
    target.column(rawDf.columns[0]).sort()  # ASC -> DESC

    target.cell(0, 1).click()
    test.send_keys(Keys.BACKSPACE)
    test.send_keys(Keys.ENTER)

    assert target.cell(0, 1).get_text() == ""
    assert test.get_log_errors() == []


@pytest.mark.skip(reason="https://github.com/plotly/dash-table/issues/700")
@pytest.mark.parametrize("props", read_write_modes)
def test_tbst021_sorted_table_delete_cell_updates_while_selected(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.column(rawDf.columns[0]).sort()  # None -> ASC
    target.column(rawDf.columns[0]).sort()  # ASC -> DESC

    target.cell(0, 1).click()
    test.send_keys(Keys.BACKSPACE)

    assert target.cell(0, 1).get_text() == ""
    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", read_write_modes)
def test_tbst022_sorted_table_delete_multiple_cells(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.column(rawDf.columns[0]).sort()  # None -> ASC
    target.column(rawDf.columns[0]).sort()  # ASC -> DESC

    target.cell(0, 1).click()
    with test.hold(Keys.SHIFT):
        ActionChains(test.driver).send_keys(Keys.DOWN).send_keys(Keys.RIGHT).perform()

    ActionChains(test.driver).send_keys(Keys.BACKSPACE).send_keys(Keys.ENTER).perform()

    for row in range(2):
        for col in range(1, 3):
            assert target.cell(row, col).get_text() == ""

    assert test.get_log_errors() == []


@pytest.mark.skip(reason="https://github.com/plotly/dash-table/issues/700")
@pytest.mark.parametrize("props", read_write_modes)
def test_tbst023_sorted_table_delete_multiple_cells_while_selected(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.column(rawDf.columns[0]).sort()  # None -> ASC
    target.column(rawDf.columns[0]).sort()  # ASC -> DESC

    target.cell(0, 1).click()
    with test.hold(Keys.SHIFT):
        ActionChains(test.driver).send_keys(Keys.DOWN).send_keys(Keys.RIGHT).perform()

    ActionChains(test.driver).send_keys(Keys.BACKSPACE).perform()

    for row in range(2):
        for col in range(1, 3):
            assert target.cell(row, col).get_text() == ""

    assert test.get_log_errors() == []


def test_tbst024_row_selectable_filter_action(test):
    app = dash.Dash(__name__)

    app.layout = DataTable(
        id="test-table",
        row_selectable="single",
        filter_action="native",
    )

    test.start_server(app)

    test.wait_for_element("#test-table")

    assert test.get_log_errors() == []
