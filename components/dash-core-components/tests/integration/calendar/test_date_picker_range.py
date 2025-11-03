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

    date_picker = dash_dcc.find_element("#dps-initial-month")
    date_picker.click()

    dash_dcc.wait_for_text_to_equal(
        ".dash-datepicker .dash-dropdown-value",
        "October",
        1,
    )

    year_input = dash_dcc.find_element(".dash-datepicker .dash-input-container input")
    assert year_input.get_attribute("value") == "2019"

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

    date_picker = dash_dcc.find_element("#dps-initial-month")
    date_picker.click()

    dash_dcc.wait_for_text_to_equal(
        ".dash-datepicker .dash-dropdown-value",
        "January",
        1,
    )

    year_input = dash_dcc.find_element(".dash-datepicker .dash-input-container input")
    assert year_input.get_attribute("value") == "2010"

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

    date_picker = dash_dcc.find_element("#dps-initial-month")
    date_picker.click()

    dash_dcc.wait_for_text_to_equal(
        ".dash-datepicker .dash-dropdown-value",
        "August",
        1,
    )

    year_input = dash_dcc.find_element(".dash-datepicker .dash-input-container input")
    assert year_input.get_attribute("value") == "2019"

    assert dash_dcc.get_logs() == []


def test_dtpr004_max_and_min_dates_are_clickable(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dps-initial-month",
                display_format="MM/DD/YYYY",
                start_date=datetime(2021, 1, 11),
                end_date=datetime(2021, 1, 19),
                max_date_allowed=datetime(2021, 1, 20),
                min_date_allowed=datetime(2021, 1, 10),
            )
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.select_date_range("dps-initial-month", (10, 20))

    start_date = dash_dcc.find_element(".dash-datepicker-start-date")
    assert start_date.get_attribute("value") == "01/10/2021"

    end_date = dash_dcc.find_element(".dash-datepicker-end-date")
    assert end_date.get_attribute("value") == "01/20/2021"

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
        style={"width": "50%"},
    )
    dash_dcc.start_server(app)
    date = dash_dcc.find_element("#dpr")
    assert not date.get_attribute("value")
    assert not any(
        dash_dcc.select_date_range("dpr", day_range=(10, 11))
    ), "Disabled days should not be clickable"

    date.click()
    assert all(
        dash_dcc.select_date_range("dpr", day_range=(1, 2))
    ), "Other days should be clickable"

    # open datepicker to take snapshot
    date.click()
    dash_dcc.percy_snapshot("dtpr005 - disabled days")
