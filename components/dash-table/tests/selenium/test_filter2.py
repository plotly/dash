import dash
from dash.dependencies import Input, Output

from utils import get_props

from dash.dash_table import DataTable
from dash.html import Div, Button
from selenium.webdriver.common.action_chains import ActionChains
import pytest


def get_app(props=dict(), special=False, clear=False):
    app = dash.Dash(__name__)

    baseProps = get_props(rows=200)

    if special:
        for c in baseProps.get("columns"):
            if c["id"] == "bbb":
                c["id"] = "b+bb"
            elif c["id"] == "ccc":
                c["id"] = "c cc"
            elif c["id"] == "ddd":
                c["id"] = "d:dd"
            elif c["id"] == "eee":
                c["id"] = "e-ee"
            elif c["id"] == "fff":
                c["id"] = "f_ff"
            elif c["id"] == "ggg":
                c["id"] = "g.gg"

        for i in range(len(baseProps["data"])):
            d = baseProps["data"][i]
            d["b+bb"] = d["bbb"]
            d["c cc"] = d["ccc"]
            d["d:dd"] = d["ddd"]
            d["e-ee"] = d["eee"]
            d["f_ff"] = d["fff"]
            d["g.gg"] = d["ggg"]

    baseProps.update(dict(filter_action="native"))
    baseProps.update(props)

    if clear:
        app.layout = Div(
            [DataTable(**baseProps), Button(id="btn", children=["Clear filters"])]
        )

        @app.callback(Output("table", "filter_query"), Input("btn", "n_clicks"))
        def get_filter(n_clicks):
            return ""

    else:
        app.layout = DataTable(**baseProps)

    return app


def test_spfi001_can_filter_columns_with_special_characters(test):
    test.start_server(get_app(special=True))

    target = test.table("table")

    target.column("b+bb").filter_value("Wet")
    target.column("c cc").filter_value("gt 90")
    target.column("d:dd").filter_value("lt 12500")
    target.column("e-ee").filter_value("is prime")
    target.column("f_ff").filter_value("le 106")
    target.column("g.gg").filter_value("gt 1000")
    target.column("b+bb").filter_click()

    assert target.cell(0, "rows").get_text() == "101"
    assert not target.cell(1, "rows").exists()

    assert target.column("b+bb").filter_value() == "Wet"
    assert target.column("c cc").filter_value() == "gt 90"
    assert target.column("d:dd").filter_value() == "lt 12500"
    assert target.column("e-ee").filter_value() == "is prime"
    assert target.column("f_ff").filter_value() == "le 106"
    assert target.column("g.gg").filter_value() == "gt 1000"

    assert test.get_log_errors() == []


def test_spfi002_handles_hovering(test):
    test.start_server(get_app())

    target = test.table("table")

    target.column("ccc").filter_value("gt 100")
    target.column("ddd").filter_value("lt 20000")

    ac = ActionChains(test.driver)
    ac.move_to_element(target.column("eee").filter())
    ac.perform()

    assert target.column("ccc").filter_value() == "gt 100"
    assert target.column("ddd").filter_value() == "lt 20000"
    assert test.get_log_errors() == []


def test_spfi003_handles_invalid_queries(test):
    test.start_server(get_app())

    target = test.table("table")

    ccc0 = target.cell(0, "ccc").get_text()
    ccc1 = target.cell(1, "ccc").get_text()

    target.column("ddd").filter_value('"20 a000')
    target.column("eee").filter_value("is prime2")
    target.column("bbb").filter_value('! !"')
    target.column("ccc").filter_click()

    assert target.cell(0, "ccc").get_text() == ccc0
    assert target.cell(1, "ccc").get_text() == ccc1

    assert target.column("ddd").filter_value() == '"20 a000'
    assert target.column("eee").filter_value() == "is prime2"
    assert target.column("bbb").filter_value() == '! !"'

    assert target.column("ddd").filter_invalid()
    assert target.column("eee").filter_invalid()
    assert target.column("bbb").filter_invalid()
    assert test.get_log_errors() == []


def test_spfi004_defaults_to_contains_on_text_column(test):
    test.start_server(get_app())

    target = test.table("table")
    target.column("bbb").filter_value("Tr")
    target.column("ccc").filter_click()

    assert target.column("bbb").filter_value() == "Tr"
    assert target.cell(0, "bbb-readonly").get_text() == "label Tropical Beaches"
    assert test.get_log_errors() == []


def test_spfi005_defaults_to_equal_on_numeric_column(test):
    test.start_server(get_app())

    target = test.table("table")
    target.column("ccc").filter_value("100")
    target.column("bbb").filter_click()

    assert target.column("ccc").filter_value() == "100"
    assert target.cell(0, "ccc").get_text() == "100"
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "filter,success", [("<=5", True), ("<= 5", True), ("le 5", True), ("le5", False)]
)
def test_spfi006_relational_operator_space(test, filter, success):
    test.start_server(get_app())

    target = test.table("table")
    target.column("ccc").filter_value(filter)
    target.column("bbb").filter_click()

    assert target.column("ccc").filter_value() == filter

    if success:
        assert target.cell(0, "ccc").get_text() == "0"
        assert target.cell(1, "ccc").get_text() == "1"
        assert target.cell(2, "ccc").get_text() == "2"
        assert target.cell(3, "ccc").get_text() == "3"
        assert target.cell(4, "ccc").get_text() == "4"
    else:
        assert not target.cell(0, "ccc").exists()

    assert test.get_log_errors() == []


def test_spfi007_invalid_and_valid_no_reset(test):
    test.start_server(get_app())

    target = test.table("table")
    target.column("ccc").filter_value("is prime2")
    target.column("ddd").filter_value("lt 20000")
    target.column("eee").filter_click()

    assert target.column("ccc").filter_value() == "is prime2"
    assert target.column("ddd").filter_value() == "lt 20000"
    assert test.get_log_errors() == []


def test_spfi008_reset_updates(test):
    test.start_server(get_app(clear=True))

    target = test.table("table")
    ccc0 = target.cell(0, "ccc").get_text()
    ccc1 = target.cell(1, "ccc").get_text()

    target.column("bbb").filter_value("Wet")
    target.column("ccc").filter_value("gt 80")
    target.column("ddd").filter_value("lt 12500")
    target.column("eee").filter_value("is prime")
    target.column("ccc").filter_click()

    assert target.cell(0, "ccc").get_text() == "89"
    assert target.cell(1, "ccc").get_text() == "97"

    assert target.column("bbb").filter_value() == "Wet"
    assert target.column("ccc").filter_value() == "gt 80"
    assert target.column("ddd").filter_value() == "lt 12500"
    assert target.column("eee").filter_value() == "is prime"

    test.find_element("#btn").click()

    assert target.cell(0, "ccc").get_text() == ccc0
    assert target.cell(1, "ccc").get_text() == ccc1

    assert target.column("bbb").filter_value() == ""
    assert target.column("ccc").filter_value() == ""
    assert target.column("ddd").filter_value() == ""
    assert target.column("eee").filter_value() == ""
    assert test.get_log_errors() == []
