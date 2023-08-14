import dash

from utils import get_props

from dash.dash_table import DataTable


def get_app(props=dict()):
    app = dash.Dash(__name__)

    baseProps = get_props()

    for c in baseProps.get("columns"):
        c["clearable"] = True
        c["deletable"] = True
        c["hideable"] = "last"
        c["selectable"] = True

    baseProps["column_selectable"] = "multi"
    baseProps["filter_action"] = "native"
    baseProps["merge_duplicate_headers"] = True

    # first col is normally only 60px, make it wider since we're adding
    # all these actions and need to interact with them
    baseProps["style_cell_conditional"][0].update(width=120, maxWidth=120, minWidth=120)
    baseProps.update(props)

    app.layout = DataTable(**baseProps)

    return app


def test_colm001_can_delete(test):
    test.start_server(get_app())

    target = test.table("table")

    assert target.column(0).get_text(2) == "rows"
    assert target.column(1).get_text(0) == "City"
    assert target.column(1).get_text(1) == "Canada"
    assert target.column(1).get_text(2) == "Toronto"

    target.column("rows").delete(0)

    assert target.column(0).get_text(0) == "City"
    assert target.column(0).get_text(1) == "Canada"
    assert target.column(0).get_text(2) == "Toronto"

    # Remove Canada
    target.column("ccc").delete(1)

    assert target.column(0).get_text(0) == "City"
    assert target.column(0).get_text(1) == "America"
    assert target.column(0).get_text(2) == "New York City"

    # Remove Boston
    target.column("fff").delete(2)

    assert target.column(0).get_text(0) == "City"
    assert target.column(0).get_text(1) == "America"
    assert target.column(0).get_text(2) == "New York City"
    assert target.column(1).get_text(1) == "France"
    assert target.column(1).get_text(2) == "Paris"

    assert test.get_log_errors() == []


def test_colm002_keep_hidden_on_delete(test):
    test.start_server(get_app())

    target = test.table("table")
    target.column(4).hide(2)  # Boston
    target.column(2).hide(2)  # Montreal
    target.column("ccc").delete(0)  # City

    toggle = target.toggle_columns()

    toggle.open()
    assert toggle.is_opened()

    hidden = toggle.get_hidden()
    assert len(hidden) == 2

    for el in hidden:
        el.click()

    assert len(toggle.get_hidden()) == 0


def test_colm003_can_clear(test):
    test.start_server(get_app())

    target = test.table("table")

    for i in range(5):
        target.column(i).filter_value("is num")

    target.column("rows").clear(0)  # rows
    target.column("ccc").clear(1)  # Canada
    target.column("fff").clear(2)  # Boston

    assert target.cell(0, "rows").get_text() == ""
    assert target.cell(0, "ccc").get_text() == ""
    assert target.cell(0, "ddd").get_text() == ""
    assert target.cell(0, "eee").get_text() == "0"
    assert target.cell(0, "fff").get_text() == ""

    assert target.column("rows").filter_value() == ""
    assert target.column("ccc").filter_value() == ""
    assert target.column("ddd").filter_value() == ""
    assert target.column("eee").filter_value() == "is num"
    assert target.column("fff").filter_value() == ""


def test_colm004_can_hide(test):
    test.start_server(get_app())

    target = test.table("table")

    assert target.column(0).get_text(2) == "rows"
    target.column("rows").hide(2)

    assert target.column(0).get_text(2) == "Toronto"
    target.column("ccc").hide(2)  # Toronto

    assert target.column(0).get_text(2) == "Montréal"
    target.column("ddd").hide(2)  # Montreal

    assert target.column(0).get_text(2) == "New York City"

    toggle = target.toggle_columns()

    toggle.open()
    assert toggle.is_opened()

    hidden = toggle.get_hidden()
    assert len(hidden) == 3

    for el in hidden:
        el.click()

    toggle.close()

    assert target.column(0).get_text(2) == "rows"
    assert target.column(1).get_text(2) == "Toronto"
    assert target.column(2).get_text(2) == "Montréal"


def test_colm005_dont_clear_hidden(test):
    test.start_server(get_app())

    target = test.table("table")

    # initial state
    assert target.cell(0, "ccc").get_text() == "0"
    assert target.cell(0, "ddd").get_text() == "0"
    assert target.cell(0, "eee").get_text() == "0"
    assert target.cell(0, "fff").get_text() == "1"
    assert target.cell(0, "ggg").get_text() == "0"

    # hide Montreal and Boston
    target.column("ddd").hide(2)
    target.column("fff").hide(2)

    # clear all cities
    target.column("ccc").clear(0)

    toggle = target.toggle_columns()

    toggle.open()
    assert toggle.is_opened()

    hidden = toggle.get_hidden()
    assert len(hidden) == 2

    for el in hidden:
        el.click()

    toggle.close()

    assert target.cell(0, "ccc").get_text() == ""
    assert target.cell(0, "ddd").get_text() == "0"
    assert target.cell(0, "eee").get_text() == ""
    assert target.cell(0, "fff").get_text() == "1"
    assert target.cell(0, "ggg").get_text() == ""


def test_colm006_multi_select(test):
    test.start_server(get_app(dict(column_selectable="multi")))

    target = test.table("table")

    target.column("ccc").select(0)

    assert not target.column("rows").is_selected(0)
    assert not target.column("rows").is_selected(1)
    assert not target.column("rows").is_selected(2)

    for c in ["ccc", "ddd", "eee", "fff", "ggg"]:
        for r in range(3):
            if target.column(c).exists(r):
                assert target.column(c).is_selected(r)

    target.column("rows").select(0)

    for c in ["rows" "ccc", "ddd", "eee", "fff", "ggg"]:
        for r in range(3):
            if target.column(c).exists(r):
                assert target.column(c).is_selected(r)

    target.column("rows").select(0)
    target.column("ccc").select(0)

    for c in ["rows" "ccc", "ddd", "eee", "fff", "ggg"]:
        for r in range(3):
            if target.column(c).exists(r):
                assert not target.column(c).is_selected(r)


def test_colm007_single_select(test):
    test.start_server(get_app(dict(column_selectable="single")))

    target = test.table("table")

    for select in [
        ("ccc", 0),
        ("ccc", 1),
        ("ccc", 2),
        ("rows", 0),
    ]:
        target.column(select[0]).select(select[1])

        for c in ["rows" "ccc", "ddd", "eee", "fff", "ggg"]:
            for r in range(3):
                if target.column(c).exists(r):
                    assert target.column(c).is_selected(r) == (
                        c == select[0] and r == select[1]
                    )


def test_colm008_top_row_by_subset(test):
    test.start_server(get_app(dict(column_selectable="multi")))

    target = test.table("table")

    target.column("ccc").select(1)
    target.column("ggg").select(1)

    for c in ["rows", "eee", "fff"]:
        for r in range(3):
            if target.column(c).exists(r):
                assert not target.column(c).is_selected(r)

    for c in ["ccc", "ddd", "ggg"]:
        for r in range(1, 3):
            if target.column(c).exists(r):
                assert target.column(c).is_selected(r)

    target.column("eee").select(1)

    for c in ["rows"]:
        for r in range(3):
            if target.column(c).exists(r):
                assert not target.column(c).is_selected(r)

    for c in ["ccc", "ddd", "eee", "fff", "ggg"]:
        for r in range(3):
            if target.column(c).exists(r):
                assert target.column(c).is_selected(r)


def test_colm009_newline_id(test):
    app = dash.Dash(__name__)

    columns = [
        {"name": "aaabbb", "id": "aaa\nbbb"},
        {"name": "cccddd", "id": "ccc\nddd"},
    ]
    data = [{columns[c]["id"]: r + (3 * c) + 1 for c in [0, 1]} for r in [0, 1, 2]]
    tooltip_data = [{k: str(v * 11) for k, v in row.items()} for row in data]

    app.layout = DataTable(
        id="table", columns=columns, data=data, tooltip_data=tooltip_data
    )

    test.start_server(app)

    target = test.table("table")
    cell = target.cell(1, 1)

    target.is_ready()
    cell.move_to()
    # note first I tried tooltip.exists() and tooltip.get_text() like in ttip001
    # but that didn't work? didn't wait for it perhaps?
    test.wait_for_text_to_equal(".dash-tooltip", "55")
    assert test.get_log_errors() == []
