import dash
from dash.dependencies import Input, Output

from dash import html
from dash.dash_table import DataTable

from selenium.webdriver.common.keys import Keys

import json
import time
import pandas as pd

url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
rawDf = pd.read_csv(url, nrows=100)
rawDf["id"] = rawDf.index + 3000

df = rawDf.to_dict("records")

props = [
    "active_cell",
    "start_cell",
    "end_cell",
    "selected_cells",
    "selected_rows",
    "selected_row_ids",
    "derived_viewport_selected_rows",
    "derived_viewport_selected_row_ids",
    "derived_virtual_selected_rows",
    "derived_virtual_selected_row_ids",
    "derived_viewport_indices",
    "derived_viewport_row_ids",
    "derived_virtual_indices",
    "derived_virtual_row_ids",
]


def get_app():
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            DataTable(
                id="table",
                columns=[{"name": i, "id": i} for i in rawDf.columns],
                data=df,
                editable=True,
                filter_action="native",
                fixed_columns={"headers": True},
                fixed_rows={"headers": True},
                page_action="native",
                page_size=10,
                row_deletable=True,
                row_selectable=True,
                sort_action="native",
                style_cell=dict(width=100, min_width=100, max_width=100),
            ),
            html.Div(id="props_container", children=["Nothing yet"]),
        ]
    )

    @app.callback(
        Output("props_container", "children"), [Input("table", prop) for prop in props]
    )
    def show_props(*args):
        # return 'Something yet!'
        # print('show props')
        return html.Table(
            [
                html.Tr(
                    [
                        html.Td(prop),
                        html.Td(
                            json.dumps(val) if val is not None else "None", id=prop
                        ),
                    ]
                )
                for prop, val in zip(props, args)
            ]
        )

    return app


def test_tdrp001_select_rows(test):
    test.start_server(get_app())

    target = test.table("table")

    target.row(0).select()
    target.row(1).select()

    assert test.find_element("#active_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#start_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#end_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_cells").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_rows").get_attribute("innerHTML") == json.dumps(
        list(range(2))
    )
    assert test.find_element("#selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3002)))

    assert test.find_element("#derived_viewport_selected_rows").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(2)))
    assert test.find_element("#derived_viewport_selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3002)))
    assert test.find_element("#derived_viewport_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(10)))
    assert test.find_element("#derived_viewport_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3010)))

    assert test.find_element("#derived_virtual_selected_rows").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(2)))
    assert test.find_element("#derived_virtual_selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3002)))
    assert test.find_element("#derived_virtual_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(100)))
    assert test.find_element("#derived_virtual_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3100)))
    assert test.get_log_errors() == []


def test_tdrp002_select_cell(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(0, 0).click()

    active = dict(row=0, column=0, column_id=rawDf.columns[0], row_id=3000)

    time.sleep(1)

    assert test.find_element("#active_cell").get_attribute("innerHTML") == json.dumps(
        active
    )
    assert test.find_element("#start_cell").get_attribute("innerHTML") == json.dumps(
        active
    )
    assert test.find_element("#end_cell").get_attribute("innerHTML") == json.dumps(
        active
    )
    assert test.find_element("#selected_cells").get_attribute(
        "innerHTML"
    ) == json.dumps([active])
    assert test.find_element("#selected_rows").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_row_ids").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]

    assert test.find_element("#derived_viewport_selected_rows").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_viewport_selected_row_ids").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_viewport_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(10)))
    assert test.find_element("#derived_viewport_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3010)))

    assert test.find_element("#derived_virtual_selected_rows").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_virtual_selected_row_ids").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_virtual_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(100)))
    assert test.find_element("#derived_virtual_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3100)))
    assert test.get_log_errors() == []


def test_tdrp003_select_cells(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(0, 0).click()
    with test.hold(Keys.SHIFT):
        test.send_keys(Keys.DOWN + Keys.DOWN + Keys.RIGHT + Keys.RIGHT)

    active = dict(row=0, column=0, column_id=rawDf.columns[0], row_id=3000)

    selected = []
    for row in range(3):
        for col in range(3):
            selected.append(
                dict(
                    row=row, column=col, column_id=rawDf.columns[col], row_id=row + 3000
                )
            )

    assert test.find_element("#active_cell").get_attribute("innerHTML") == json.dumps(
        active
    )
    assert test.find_element("#start_cell").get_attribute("innerHTML") == json.dumps(
        selected[0]
    )
    assert test.find_element("#end_cell").get_attribute("innerHTML") == json.dumps(
        selected[-1]
    )
    assert test.find_element("#selected_cells").get_attribute(
        "innerHTML"
    ) == json.dumps(selected)
    assert test.find_element("#selected_rows").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_row_ids").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]

    assert test.find_element("#derived_viewport_selected_rows").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_viewport_selected_row_ids").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_viewport_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(10)))
    assert test.find_element("#derived_viewport_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3010)))

    assert test.find_element("#derived_virtual_selected_rows").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_virtual_selected_row_ids").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_virtual_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(100)))
    assert test.find_element("#derived_virtual_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3100)))

    # reduce selection
    with test.hold(Keys.SHIFT):
        test.send_keys(Keys.UP + Keys.LEFT)

    selected = []
    for row in range(2):
        for col in range(2):
            selected.append(
                dict(
                    row=row, column=col, column_id=rawDf.columns[col], row_id=row + 3000
                )
            )

    assert test.find_element("#active_cell").get_attribute("innerHTML") == json.dumps(
        active
    )
    assert test.find_element("#start_cell").get_attribute("innerHTML") == json.dumps(
        selected[0]
    )
    assert test.find_element("#end_cell").get_attribute("innerHTML") == json.dumps(
        selected[-1]
    )
    assert test.find_element("#selected_cells").get_attribute(
        "innerHTML"
    ) == json.dumps(selected)
    assert test.find_element("#selected_rows").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_row_ids").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]

    assert test.find_element("#derived_viewport_selected_rows").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_viewport_selected_row_ids").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_viewport_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(10)))
    assert test.find_element("#derived_viewport_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3010)))

    assert test.find_element("#derived_virtual_selected_rows").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_virtual_selected_row_ids").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_virtual_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(100)))
    assert test.find_element("#derived_virtual_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3100)))
    assert test.get_log_errors() == []


def test_tdrp004_navigate_selected_cells(test):
    test.start_server(get_app())

    target = test.table("table")

    target.cell(0, 0).click()
    with test.hold(Keys.SHIFT):
        test.send_keys(Keys.DOWN + Keys.DOWN + Keys.RIGHT + Keys.RIGHT)

    selected = []
    for row in range(3):
        for col in range(3):
            selected.append(
                dict(
                    row=row, column=col, column_id=rawDf.columns[col], row_id=row + 3000
                )
            )

    for row in range(3):
        for col in range(3):
            # active = dict(
            #     row=row, column=col, column_id=rawDf.columns[col], row_id=row + 3000
            # )

            # assert test.find_element("#active_cell").get_attribute(
            #     "innerHTML"
            # ) == json.dumps(active)
            assert test.find_element("#start_cell").get_attribute(
                "innerHTML"
            ) == json.dumps(selected[0])
            assert test.find_element("#end_cell").get_attribute(
                "innerHTML"
            ) == json.dumps(selected[-1])
            assert test.find_element("#selected_cells").get_attribute(
                "innerHTML"
            ) == json.dumps(selected)
            assert test.find_element("#selected_rows").get_attribute("innerHTML") in [
                "None",
                json.dumps([]),
            ]
            assert test.find_element("#selected_row_ids").get_attribute(
                "innerHTML"
            ) in ["None", json.dumps([])]

            assert test.find_element("#derived_viewport_selected_rows").get_attribute(
                "innerHTML"
            ) in ["None", json.dumps([])]
            assert test.find_element(
                "#derived_viewport_selected_row_ids"
            ).get_attribute("innerHTML") in ["None", json.dumps([])]
            assert test.find_element("#derived_viewport_indices").get_attribute(
                "innerHTML"
            ) == json.dumps(list(range(10)))
            assert test.find_element("#derived_viewport_row_ids").get_attribute(
                "innerHTML"
            ) == json.dumps(list(range(3000, 3010)))

            assert test.find_element("#derived_virtual_selected_rows").get_attribute(
                "innerHTML"
            ) in ["None", json.dumps([])]
            assert test.find_element("#derived_virtual_selected_row_ids").get_attribute(
                "innerHTML"
            ) in ["None", json.dumps([])]
            assert test.find_element("#derived_virtual_indices").get_attribute(
                "innerHTML"
            ) == json.dumps(list(range(100)))
            assert test.find_element("#derived_virtual_row_ids").get_attribute(
                "innerHTML"
            ) == json.dumps(list(range(3000, 3100)))

            test.send_keys(Keys.TAB)

    assert test.get_log_errors() == []


def test_tdrp005_filtered_and_sorted_row_select(test):
    test.start_server(get_app())

    target = test.table("table")

    target.row(0).select()
    target.row(1).select()
    target.row(2).select()

    assert test.find_element("#active_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#start_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#end_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_cells").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_rows").get_attribute("innerHTML") == json.dumps(
        list(range(3))
    )
    assert test.find_element("#selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3003)))

    assert test.find_element("#derived_viewport_selected_rows").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3)))
    assert test.find_element("#derived_viewport_selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3003)))
    assert test.find_element("#derived_viewport_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(10)))
    assert test.find_element("#derived_viewport_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3010)))

    assert test.find_element("#derived_virtual_selected_rows").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3)))
    assert test.find_element("#derived_virtual_selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3003)))
    assert test.find_element("#derived_virtual_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(100)))
    assert test.find_element("#derived_virtual_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3100)))

    target.column(0).filter_value("is even")

    assert test.find_element("#active_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#start_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#end_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_cells").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_rows").get_attribute("innerHTML") == json.dumps(
        list(range(3))
    )
    assert test.find_element("#selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3003)))

    assert test.find_element("#derived_viewport_selected_rows").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(0, 2)))
    assert test.find_element("#derived_viewport_selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3003, 2)))
    assert test.find_element("#derived_viewport_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(0, 20, 2)))
    assert test.find_element("#derived_viewport_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3020, 2)))

    assert test.find_element("#derived_virtual_selected_rows").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(0, 2)))
    assert test.find_element("#derived_virtual_selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3003, 2)))
    assert test.find_element("#derived_virtual_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(0, 100, 2)))
    assert test.find_element("#derived_virtual_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3100, 2)))

    target.column(rawDf.columns[0]).sort()  # None -> ASC
    target.column(rawDf.columns[0]).sort()  # ASC -> DESC

    assert test.find_element("#active_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#start_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#end_cell").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_cells").get_attribute("innerHTML") in [
        "None",
        json.dumps([]),
    ]
    assert test.find_element("#selected_rows").get_attribute("innerHTML") == json.dumps(
        list(range(3))
    )
    assert test.find_element("#selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3003)))

    assert test.find_element("#derived_viewport_selected_rows").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_viewport_selected_row_ids").get_attribute(
        "innerHTML"
    ) in ["None", json.dumps([])]
    assert test.find_element("#derived_viewport_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(80, 100, 2))[::-1])
    assert test.find_element("#derived_viewport_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3080, 3100, 2))[::-1])

    assert test.find_element("#derived_virtual_selected_rows").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(48, 50))[::-1])
    assert test.find_element("#derived_virtual_selected_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3003, 2)))
    assert test.find_element("#derived_virtual_indices").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(0, 100, 2))[::-1])
    assert test.find_element("#derived_virtual_row_ids").get_attribute(
        "innerHTML"
    ) == json.dumps(list(range(3000, 3100, 2))[::-1])
    assert test.get_log_errors() == []
