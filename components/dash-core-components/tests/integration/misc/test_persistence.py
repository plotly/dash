# -*- coding: utf-8 -*-
import json
from selenium.webdriver.common.keys import Keys

from dash import Dash, Input, Output, dcc, html


def test_msps001_basic_persistence(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Checklist(
                id="checklist",
                options=[
                    {"label": "Slow 🐢", "value": "🐢"},
                    {"label": "Fast 🏎️", "value": "🏎️"},
                    {"label": "Faster 🚀", "value": "🚀"},
                ],
                value=["🏎️"],
                persistence=True,
            ),
            dcc.DatePickerRange(
                id="datepickerrange",
                start_date="2017-08-21",
                end_date="2024-04-08",
                start_date_id="start_date",
                end_date_id="end_date",
                initial_visible_month="2019-05-01",
                persistence=True,
            ),
            dcc.DatePickerSingle(
                id="datepickersingle", date="2019-01-01", persistence=True
            ),
            dcc.Dropdown(
                id="dropdownsingle",
                options=[
                    {"label": "One 1️⃣", "value": "1️⃣"},
                    {"label": "Two 2️⃣", "value": "2️⃣"},
                    {"label": "Three 3️⃣", "value": "3️⃣"},
                ],
                value="2️⃣",
                persistence=True,
            ),
            dcc.Dropdown(
                id="dropdownmulti",
                options=[
                    {"label": "Four 4️⃣", "value": "4️⃣"},
                    {"label": "Five 5️⃣", "value": "5️⃣"},
                    {"label": "Six 6️⃣", "value": "6️⃣"},
                ],
                value=["4️⃣"],
                multi=True,
                persistence=True,
            ),
            dcc.Input(id="input", value="yes", persistence=True),
            dcc.RadioItems(
                id="radioitems",
                options=[
                    {"label": "Red", "value": "r"},
                    {"label": "Green", "value": "g"},
                    {"label": "Blue", "value": "b"},
                ],
                value="b",
                persistence=True,
            ),
            dcc.RangeSlider(
                id="rangeslider", min=0, max=10, step=1, value=[3, 7], persistence=True
            ),
            dcc.Slider(id="slider", min=20, max=30, step=1, value=25, persistence=True),
            dcc.Tabs(
                id="tabs",
                children=[
                    dcc.Tab(label="Eh?", children="Tab A", value="A"),
                    dcc.Tab(label="Bee", children="Tab B", value="B"),
                    dcc.Tab(label="Sea", children="Tab C", value="C"),
                ],
                value="A",
                persistence=True,
            ),
            dcc.Textarea(id="textarea", value="knock knock", persistence=True),
            html.Div(id="settings"),
        ]
    )

    @app.callback(
        Output("settings", "children"),
        [
            Input("checklist", "value"),
            Input("datepickerrange", "start_date"),
            Input("datepickerrange", "end_date"),
            Input("datepickersingle", "date"),
            Input("dropdownsingle", "value"),
            Input("dropdownmulti", "value"),
            Input("input", "value"),
            Input("radioitems", "value"),
            Input("rangeslider", "value"),
            Input("slider", "value"),
            Input("tabs", "value"),
            Input("textarea", "value"),
        ],
    )
    def make_output(*args):
        return json.dumps(args)

    initial_settings = [
        ["🏎️"],
        "2017-08-21",
        "2024-04-08",
        "2019-01-01",
        "2️⃣",
        ["4️⃣"],
        "yes",
        "b",
        [3, 7],
        25,
        "A",
        "knock knock",
    ]

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#settings", json.dumps(initial_settings))

    dash_dcc.find_element("#checklist label:last-child input").click()  # 🚀

    dash_dcc.select_date_range("datepickerrange", day_range=(4,))
    dash_dcc.select_date_range("datepickerrange", day_range=(14,), start_first=False)

    dash_dcc.find_element("#datepickersingle input").click()
    dash_dcc.select_date_single("datepickersingle", day="20")

    dash_dcc.find_element("#dropdownsingle .Select-input input").send_keys(
        "one" + Keys.ENTER
    )

    dash_dcc.find_element("#dropdownmulti .Select-input input").send_keys(
        "six" + Keys.ENTER
    )

    dash_dcc.find_element("#input").send_keys(" maybe")

    dash_dcc.find_element("#radioitems label:first-child input").click()  # red

    range_slider = dash_dcc.find_element("#rangeslider")
    dash_dcc.click_at_coord_fractions(range_slider, 0.5, 0.25)  # 5
    dash_dcc.click_at_coord_fractions(range_slider, 0.8, 0.25)  # 8

    slider = dash_dcc.find_element("#slider")
    dash_dcc.click_at_coord_fractions(slider, 0.2, 0.25)  # 22

    dash_dcc.find_element("#tabs .tab:last-child").click()  # C

    dash_dcc.find_element("#textarea").send_keys(Keys.ENTER + "who's there?")

    edited_settings = [
        ["🏎️", "🚀"],
        "2019-05-04",
        "2019-05-14",
        "2019-01-20",
        "1️⃣",
        ["4️⃣", "6️⃣"],
        "yes maybe",
        "r",
        [5, 8],
        22,
        "C",
        "knock knock\nwho's there?",
    ]

    dash_dcc.wait_for_text_to_equal("#settings", json.dumps(edited_settings))

    # now reload the page - all of these settings should persist
    dash_dcc.wait_for_page()
    dash_dcc.wait_for_text_to_equal("#settings", json.dumps(edited_settings))

    assert dash_dcc.get_logs() == []
