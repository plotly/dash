import dash

from dash.dash_table import DataTable

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


@pytest.mark.parametrize(
    "filter_case_options,column_case_filter_options",
    [
        ("sensitive", None),
        ("sensitive", None),
        ("sensitive", None),
        ("insensitive", None),
        ("sensitive", "insensitive"),
        ("insensitive", "sensitive"),
    ],
)
def test_filt002_sensitivity(test, filter_case_options, column_case_filter_options):
    props = dict(
        id="table",
        data=[dict(a="abc", b="abc", c="abc"), dict(a="ABC", b="ABC", c="ABC")],
        columns=[
            dict(
                id="a",
                name="a",
                filter_options=dict(case=column_case_filter_options)
                if column_case_filter_options is not None
                else None,
                type="any",
            ),
            dict(
                id="b",
                name="b",
                filter_options=dict(case=column_case_filter_options)
                if column_case_filter_options is not None
                else None,
                type="text",
            ),
            dict(
                id="c",
                name="c",
                filter_options=dict(case=column_case_filter_options)
                if column_case_filter_options is not None
                else None,
                type="numeric",
            ),
        ],
        filter_action="native",
        filter_options=dict(case=filter_case_options)
        if filter_case_options is not None
        else None,
        style_cell=dict(width=100, min_width=100, max_width=100),
    )

    sensitivity = (
        filter_case_options
        if column_case_filter_options is None
        else column_case_filter_options
    )

    test.start_server(get_app(props))

    target = test.table("table")

    # any -> implicit contains
    target.column("a").filter_value("A")
    if sensitivity == "sensitive":
        assert target.cell(0, "a").get_text() == "ABC"
        assert not target.cell(1, "a").exists()
    else:
        assert target.cell(0, "a").get_text() == "abc"
        assert target.cell(1, "a").get_text() == "ABC"

    target.column("a").filter_value("a")
    if sensitivity == "sensitive":
        assert target.cell(0, "a").get_text() == "abc"
        assert not target.cell(1, "a").exists()
    else:
        assert target.cell(0, "a").get_text() == "abc"
        assert target.cell(1, "a").get_text() == "ABC"

    # text -> implicit contains
    target.column("a").filter_value("")
    target.column("b").filter_value("A")
    if sensitivity == "sensitive":
        assert target.cell(0, "b").get_text() == "ABC"
        assert not target.cell(1, "b").exists()
    else:
        assert target.cell(0, "b").get_text() == "abc"
        assert target.cell(1, "b").get_text() == "ABC"

    target.column("b").filter_value("a")
    if sensitivity == "sensitive":
        assert target.cell(0, "b").get_text() == "abc"
        assert not target.cell(1, "b").exists()
    else:
        assert target.cell(0, "b").get_text() == "abc"
        assert target.cell(1, "b").get_text() == "ABC"

    # numeric -> implicit equal
    target.column("b").filter_value("")
    target.column("c").filter_value("A")
    assert not target.cell(0, "c").exists()

    target.column("c").filter_value("a")
    assert not target.cell(0, "c").exists()

    target.column("c").filter_value("ABC")
    if sensitivity == "sensitive":
        assert target.cell(0, "c").get_text() == "ABC"
        assert not target.cell(1, "c").exists()
    else:
        assert target.cell(0, "c").get_text() == "abc"
        assert target.cell(1, "c").get_text() == "ABC"

    target.column("c").filter_value("abc")
    if sensitivity == "sensitive":
        assert target.cell(0, "c").get_text() == "abc"
        assert not target.cell(1, "c").exists()
    else:
        assert target.cell(0, "c").get_text() == "abc"
        assert target.cell(1, "c").get_text() == "ABC"


@pytest.mark.parametrize(
    "filter_case_options,column_case_filter_options",
    [
        ("sensitive", None),
        ("sensitive", None),
        ("sensitive", None),
        ("insensitive", None),
        ("sensitive", "insensitive"),
        ("insensitive", "sensitive"),
    ],
)
def test_filt003_sensitivity(test, filter_case_options, column_case_filter_options):
    column_b_filter_option = dict(placeholder_text="some descriptive text")
    if column_case_filter_options is not None:
        column_b_filter_option["case"] = column_case_filter_options

    props = dict(
        id="table",
        data=[dict(a="abc", b="abc", c="abc"), dict(a="ABC", b="ABC", c="ABC")],
        columns=[
            dict(
                id="a",
                name="a",
                filter_options=dict(case=column_case_filter_options)
                if column_case_filter_options is not None
                else None,
                type="any",
            ),
            dict(
                id="b",
                name="b",
                filter_options=column_b_filter_option,
                type="text",
            ),
            dict(
                id="c",
                name="c",
                filter_options=dict(case=column_case_filter_options)
                if column_case_filter_options is not None
                else None,
                type="numeric",
            ),
        ],
        filter_action="native",
        filter_options=dict(case=filter_case_options)
        if filter_case_options is not None
        else None,
        style_cell=dict(width=100, min_width=100, max_width=100),
    )

    sensitivity = (
        filter_case_options
        if column_case_filter_options is None
        else column_case_filter_options
    )

    test.start_server(get_app(props))

    target = test.table("table")

    target.column("a").filter_placeholder() == "filter data..."
    target.column("b").filter_placeholder() == "some descriptive text"

    target.column("a").filter_value("contains A")
    if sensitivity == "sensitive":
        assert target.cell(0, "a").get_text() == "ABC"
        assert not target.cell(1, "a").exists()
    else:
        assert target.cell(0, "a").get_text() == "abc"
        assert target.cell(1, "a").get_text() == "ABC"

    target.column("a").filter_value("contains a")
    if sensitivity == "sensitive":
        assert target.cell(0, "a").get_text() == "abc"
        assert not target.cell(1, "a").exists()
    else:
        assert target.cell(0, "a").get_text() == "abc"
        assert target.cell(1, "a").get_text() == "ABC"

    target.column("a").filter_value("")
    target.column("b").filter_value("contains A")
    if sensitivity == "sensitive":
        assert target.cell(0, "b").get_text() == "ABC"
        assert not target.cell(1, "b").exists()
    else:
        assert target.cell(0, "b").get_text() == "abc"
        assert target.cell(1, "b").get_text() == "ABC"

    target.column("b").filter_value("contains a")
    if sensitivity == "sensitive":
        assert target.cell(0, "b").get_text() == "abc"
        assert not target.cell(1, "b").exists()
    else:
        assert target.cell(0, "b").get_text() == "abc"
        assert target.cell(1, "b").get_text() == "ABC"

    target.column("b").filter_value("")
    target.column("c").filter_value("contains A")
    if sensitivity == "sensitive":
        assert target.cell(0, "c").get_text() == "ABC"
        assert not target.cell(1, "c").exists()
    else:
        assert target.cell(0, "c").get_text() == "abc"
        assert target.cell(1, "c").get_text() == "ABC"

    target.column("c").filter_value("contains a")
    if sensitivity == "sensitive":
        assert target.cell(0, "c").get_text() == "abc"
        assert not target.cell(1, "c").exists()
    else:
        assert target.cell(0, "c").get_text() == "abc"
        assert target.cell(1, "c").get_text() == "ABC"


@pytest.mark.parametrize(
    "column_placeholder_setting,table_placeholder_setting,expected_placeholder",
    [
        ("abc", None, "abc"),
        (None, "def", "def"),
        ("gah", "ijk", "gah"),
        ("", None, ""),
        (None, None, "filter data..."),
    ],
)
def test_filt004_placeholder(
    test, column_placeholder_setting, table_placeholder_setting, expected_placeholder
):
    column_filter_setting = dict(case="sensitive")
    if column_placeholder_setting is not None:
        column_filter_setting["placeholder_text"] = column_placeholder_setting

    props = dict(
        id="table",
        data=[],
        columns=[
            dict(
                id="a",
                name="a",
                type="any",
                filter_options=column_filter_setting,
            ),
        ],
        filter_action="native",
        filter_options=dict(placeholder_text=table_placeholder_setting)
        if table_placeholder_setting is not None
        else None,
    )

    test.start_server(get_app(props))
    target = test.table("table")
    assert target.column("a").filter_placeholder() == expected_placeholder
