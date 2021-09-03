from datetime import datetime

from dash import Dash, html, dcc


def test_dtpr001_initial_month_provided(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dps-initial-month",
                min_date_allowed=datetime(2010, 1, 1),
                max_date_allowed=datetime(2099, 12, 31),
                initial_visible_month=datetime(2019, 10, 28),
            )
        ]
    )

    dash_dcc.start_server(app)

    date_picker_start = dash_dcc.find_element(
        '#dps-initial-month .DateInput_input.DateInput_input_1[placeholder="Start Date"]'
    )
    date_picker_start.click()

    dash_dcc.wait_for_text_to_equal(
        "#dps-initial-month .CalendarMonth.CalendarMonth_1[data-visible=true] strong",
        "October 2019",
        1,
    )

    assert dash_dcc.get_logs() == []


def test_dtpr002_no_initial_month_min_date(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dps-initial-month",
                min_date_allowed=datetime(2010, 1, 1),
                max_date_allowed=datetime(2099, 12, 31),
            )
        ]
    )

    dash_dcc.start_server(app)

    date_picker_start = dash_dcc.find_element(
        '#dps-initial-month .DateInput_input.DateInput_input_1[placeholder="Start Date"]'
    )
    date_picker_start.click()

    dash_dcc.wait_for_text_to_equal(
        "#dps-initial-month .CalendarMonth.CalendarMonth_1[data-visible=true] strong",
        "January 2010",
    )

    assert dash_dcc.get_logs() == []


def test_dtpr003_no_initial_month_no_min_date_start_date(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dps-initial-month",
                start_date=datetime(2019, 8, 13),
                max_date_allowed=datetime(2099, 12, 31),
            )
        ]
    )

    dash_dcc.start_server(app)

    date_picker_start = dash_dcc.find_element(
        '#dps-initial-month .DateInput_input.DateInput_input_1[placeholder="Start Date"]'
    )
    date_picker_start.click()

    dash_dcc.wait_for_text_to_equal(
        "#dps-initial-month .CalendarMonth.CalendarMonth_1[data-visible=true] strong",
        "August 2019",
    )

    assert dash_dcc.get_logs() == []


def test_dtpr004_max_and_min_dates_are_clickable(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dps-initial-month",
                start_date=datetime(2021, 1, 11),
                end_date=datetime(2021, 1, 19),
                max_date_allowed=datetime(2021, 1, 20),
                min_date_allowed=datetime(2021, 1, 10),
            )
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.select_date_range("dps-initial-month", (10, 20))

    dash_dcc.wait_for_text_to_equal(
        '#dps-initial-month .DateInput_input.DateInput_input_1[placeholder="Start Date"]',
        "01/10/2021",
    )

    dash_dcc.wait_for_text_to_equal(
        '#dps-initial-month .DateInput_input.DateInput_input_1[placeholder="End Date"]',
        "01/20/2021",
    )

    assert dash_dcc.get_logs() == []


def test_dtpr005_disabled_days_arent_clickable(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Operating Date"),
            dcc.DatePickerRange(
                id="dpr",
                min_date_allowed=datetime(2021, 1, 1),
                max_date_allowed=datetime(2021, 1, 31),
                initial_visible_month=datetime(2021, 1, 1),
                disabled_days=[datetime(2021, 1, 10), datetime(2021, 1, 11)],
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
    date = dash_dcc.find_element("#dpr input")
    assert not date.get_attribute("value")
    assert not any(
        dash_dcc.select_date_range("dpr", day_range=(10, 11))
    ), "Disabled days should not be clickable"
    assert all(
        dash_dcc.select_date_range("dpr", day_range=(1, 2))
    ), "Other days should be clickable"

    # open datepicker to take snapshot
    date.click()
    dash_dcc.percy_snapshot("dtpr005 - disabled days")
