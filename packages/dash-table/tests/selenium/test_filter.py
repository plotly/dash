import dash

from dash_table import DataTable

import pytest

DATA_SIZE = 50


def get_table_defaults():
    return dict(
        id="table",
        data=[
            dict(a=1, b=11, c=111),
            dict(a=2, b=12, c=113),
            dict(a=3, b=14, c=116),
            dict(a=4, b=17, c=120),
            dict(a=5, b=21, c=125),
        ],
        columns=[
            dict(id="a", name="a"),
            dict(id="b", name="b"),
            dict(id="c", name="c"),
        ],
    )


def get_native_table():
    props = get_table_defaults()

    props["filter_action"] = "native"

    return props


def get_native_and_table():
    props = get_table_defaults()

    props["filter_action"] = dict(type="native", operator="and")

    return props


def get_native_or_table():
    props = get_table_defaults()

    props["filter_action"] = dict(type="native", operator="or")

    return props


def get_app(props):
    app = dash.Dash(__name__)
    app.layout = DataTable(**props)

    return app


@pytest.mark.parametrize(
    "props,expect",
    [
        (get_native_table(), ["4"]),
        (get_native_and_table(), ["4"]),
        (get_native_or_table(), ["1", "3", "4", "5"]),
    ],
)
def test_filt001_basic(test, props, expect):
    test.start_server(get_app(props))

    target = test.table("table")

    target.column("a").filter_value("gt 3")
    target.column("b").filter_value("is prime")
    target.column("c").filter_value("ne 113")
    target.column("a").filter_click()

    for index, value in enumerate(expect):
        assert target.cell(index, "a").get_text() == value

    assert test.get_log_errors() == []
