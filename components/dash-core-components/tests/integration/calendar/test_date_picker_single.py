from datetime import datetime, timedelta
import pandas as pd
import time

import pytest
import werkzeug

from dash import Dash, Input, Output, html, dcc, no_update


@pytest.mark.DCC652
def test_dtps001_simple_click(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Operating Date"),
            dcc.DatePickerSingle(
                id="dps",
                min_date_allowed=datetime(2010, 1, 1),
                max_date_allowed=datetime(2099, 12, 31),
                initial_visible_month=datetime.today().date() - timedelta(days=1),
                day_size=47,
            ),
        ],
        style={
            "width": "10%",
            "display": "inline-block",
            "marginLeft": 10,
            "marginRight": 10,
            "marginBottom": 10,
        },
    )
    dash_dcc.start_server(app)
    date = dash_dcc.find_element("#dps input")
    assert not date.get_attribute("value")
    assert dash_dcc.select_date_single(
        "dps", index=3
    ), "Component should be clickable to choose a valid date"

    assert dash_dcc.get_logs() == []


def test_dtps010_local_and_session_persistence(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(id="dps-local", persistence=True, day_size=47),
            dcc.DatePickerSingle(
                id="dps-session",
                persistence=True,
                persistence_type="session",
                day_size=47,
            ),
        ]
    )

    dash_dcc.start_server(app)

    assert not dash_dcc.find_element("#dps-local input").get_attribute(
        "value"
    ) and not dash_dcc.find_element("#dps-session input").get_attribute(
        "value"
    ), "component should contain no initial date"

    for idx in range(3):
        local = dash_dcc.select_date_single("dps-local", index=idx)
        session = dash_dcc.select_date_single("dps-session", index=idx)
        dash_dcc.wait_for_page()
        assert (
            dash_dcc.find_element("#dps-local input").get_attribute("value") == local
            and dash_dcc.find_element("#dps-session input").get_attribute("value")
            == session
        ), "the date value should be consistent after refresh"

    assert dash_dcc.get_logs() == []


@pytest.mark.xfail(
    condition=werkzeug.__version__ in ("2.1.0", "2.1.1"),
    reason="Bug with 204 and Transfer-Encoding",
    strict=False,
)
def test_dtps011_memory_persistence(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button(id="switch", children="Switch"), html.Div(id="out")]
    )

    @app.callback(Output("out", "children"), [Input("switch", "n_clicks")])
    def cb(clicks):
        if clicks is None:
            return no_update
        if clicks % 2 == 1:
            return [
                dcc.DatePickerSingle(
                    id="dps-memory",
                    min_date_allowed=datetime(2010, 1, 1),
                    max_date_allowed=datetime(2099, 12, 31),
                    initial_visible_month=datetime.today().date() - timedelta(days=1),
                    persistence=True,
                    persistence_type="memory",
                    day_size=47,
                ),
                dcc.DatePickerSingle(
                    id="dps-none",
                    min_date_allowed=datetime(2010, 1, 1),
                    max_date_allowed=datetime(2099, 12, 31),
                    initial_visible_month=datetime.today().date() - timedelta(days=1),
                    day_size=47,
                ),
            ]
        else:
            return "switched"

    dash_dcc.start_server(app)

    switch = dash_dcc.find_element("#switch")
    switch.click()

    memorized = dash_dcc.select_date_single("dps-memory", day="4")
    amnesiaed = dash_dcc.select_date_single("dps-none", day="11")

    switch.click()
    assert dash_dcc.wait_for_text_to_equal("#out", "switched")
    switch.click()
    assert (
        dash_dcc.find_element("#dps-memory input").get_attribute("value") == memorized
    )
    switched = dash_dcc.find_element("#dps-none input").get_attribute("value")
    assert switched != amnesiaed and switched == ""

    assert dash_dcc.get_logs() == []


def test_dtps012_initial_month(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps-initial-month",
                min_date_allowed=datetime(2010, 1, 1),
                max_date_allowed=datetime(2099, 12, 31),
            )
        ]
    )

    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#dps-initial-month")
    date_picker.click()
    dash_dcc.wait_for_text_to_equal(
        "#dps-initial-month .CalendarMonth.CalendarMonth_1[data-visible=true] strong",
        "January 2010",
    )

    assert dash_dcc.get_logs() == []


def test_dtps013_disabled_days_arent_clickable(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Operating Date"),
            dcc.DatePickerSingle(
                id="dps",
                min_date_allowed=datetime(2021, 1, 1),
                max_date_allowed=datetime(2021, 1, 31),
                initial_visible_month=datetime(2021, 1, 1),
                disabled_days=[datetime(2021, 1, 10)],
            ),
        ],
        style={
            "width": "10%",
            "display": "inline-block",
            "marginLeft": 10,
            "marginRight": 10,
            "marginBottom": 10,
        },
    )
    dash_dcc.start_server(app)
    date = dash_dcc.find_element("#dps input")
    assert not date.get_attribute("value")
    assert not dash_dcc.select_date_single(
        "dps", day=10
    ), "Disabled days should not be clickable"
    assert dash_dcc.select_date_single("dps", day=1), "Other days should be clickable"

    # open datepicker to take snapshot
    date.click()
    dash_dcc.percy_snapshot("dtps013 - disabled days")


def test_dtps0014_disabed_days_timeout(dash_dcc):
    app = Dash(__name__)

    min_date = pd.to_datetime("2010-01-01")
    max_date = pd.to_datetime("2099-01-01")
    disabled_days = [
        x for x in pd.date_range(min_date, max_date, freq="D") if x.day != 1
    ]

    app.layout = html.Div(
        [
            html.Label("Operating Date"),
            dcc.DatePickerSingle(
                id="dps",
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                disabled_days=disabled_days,
            ),
        ]
    )
    dash_dcc.start_server(app)
    date = dash_dcc.wait_for_element("#dps", timeout=5)

    """
    WebDriver click() function hangs at the time of the react code
    execution, so it necessary to check execution time.
    """
    start_time = time.time()
    date.click()
    assert time.time() - start_time < 5

    dash_dcc.wait_for_element(".SingleDatePicker_picker", timeout=5)
    assert dash_dcc.get_logs() == []
