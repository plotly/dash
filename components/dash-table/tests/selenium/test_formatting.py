import dash

from utils import get_props

from dash.dash_table import DataTable
from selenium.webdriver.common.keys import Keys


def get_app(props=dict()):
    app = dash.Dash(__name__)

    baseProps = get_props()

    for i in range(len(baseProps["data"])):
        datum = baseProps["data"][i]

        if datum["eee"] % 2 == 0:
            datum.pop("eee")
        elif datum["eee"] % 10 == 5:
            datum["eee"] = "xx-{}-xx".format(datum["eee"])

    for c in baseProps["columns"]:
        if c["id"] == "rows":
            c.update(dict(format=dict(specifier=".^5")))
        elif c["id"] == "ccc":
            c.update(
                dict(
                    format=dict(
                        locale=dict(seperate_4digits=False),
                        prefix=1000,
                        specifier=".3f",
                    )
                )
            )
        elif c["id"] == "ddd":
            c.update(
                dict(
                    format=dict(
                        locale=dict(symbol=["eq. $", ""], seperate_4digits=False),
                        nully=0,
                        specifier="$,.2f",
                    ),
                    on_change=dict(action="coerce", failure="default"),
                    validation=dict(allow_nully=True),
                )
            )
        elif c["id"] == "eee":
            c.update(
                dict(
                    format=dict(nully="N/A", specifier=""),
                    on_change=dict(action="coerce", failure="default"),
                )
            )

    baseProps.update(dict(filter_action="native"))
    baseProps.update(props)

    app.layout = DataTable(**baseProps)

    return app


def test_form001_can_edit_formatted_cells(test):
    test.start_server(get_app())

    target = test.table("table")
    cell = target.cell(0, "eee")

    assert cell.get_text() == "N/A"

    cell.click()
    test.send_keys("1" + Keys.ENTER)
    assert cell.get_text() == "1"

    cell.click()
    test.send_keys("abc" + Keys.ENTER)
    assert cell.get_text() == "N/A"
    assert test.get_log_errors() == []


def test_form002_can_copy_formatted_cells(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(3, "eee").click()
    with test.hold(Keys.SHIFT):
        test.send_keys(Keys.ARROW_DOWN + Keys.ARROW_DOWN)

    test.copy()
    target.cell(3, "ddd").click()
    test.paste()
    target.cell(3, "eee").click()

    assert target.cell(3, "ddd").get_text() == "eq. $3.00"
    assert target.cell(4, "ddd").get_text() == "eq. $0.00"
    assert target.cell(5, "ddd").get_text() == "eq. $0.00"
    assert test.get_log_errors() == []
