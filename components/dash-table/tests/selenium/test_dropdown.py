import dash

from dash.dash_table import DataTable


def get_app():
    app = dash.Dash(__name__)

    columns = [
        dict(id="a", name="a"),
        dict(id="b", name="b"),
        dict(id="c", name="c", presentation="dropdown"),
    ]

    app.layout = DataTable(
        id="table",
        columns=columns,
        dropdown=dict(
            c=dict(
                options=[
                    dict(label="Value-0", value=0),
                    dict(label="Value-1", value=1),
                    dict(label="Value-2", value=2),
                    dict(label="Value-3", value=3),
                ]
            )
        ),
        data=[dict(a=i, b=i, c=i % 4) for i in range(100)],
        editable=True,
    )

    return app


def get_page_offset(test):
    return test.driver.execute_script(
        "return document.body.getBoundingClientRect().top;"
    )


def test_drpd001_no_scroll(test):
    test.start_server(get_app())

    target = test.table("table")
    cell = target.cell(1, "c")

    yOffset = get_page_offset(test)

    cell.open_dropdown()

    assert get_page_offset(test) == yOffset
    assert test.get_log_errors() == []
