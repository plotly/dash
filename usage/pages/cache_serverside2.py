import dash
from dash import dcc, html, callback, Input, Output

import datetime

import pandas as pd
import time
import uuid

dash.register_page(__name__)
from make_cache import serverside_cache


def get_dataframe2(session_id):
    # from make_cache import serverside_cache
    @serverside_cache.memoize()
    def query_and_serialize_data2(session_id):
        # expensive or user/session-unique data processing step goes here

        # simulate a user/session-unique data processing step by generating
        # data that is dependent on time
        now = datetime.datetime.now()

        # simulate an expensive data processing task by sleeping
        time.sleep(3)

        df = pd.DataFrame(
            {
                "time": [
                    str(now - datetime.timedelta(seconds=15)),
                    str(now - datetime.timedelta(seconds=10)),
                    str(now - datetime.timedelta(seconds=5)),
                    str(now),
                ],
                "values": ["a", "b", "a", "c"],
            }
        )
        return df.to_json()

    return pd.read_json(query_and_serialize_data2(session_id))


def layout():
    session_id2 = str(uuid.uuid4())

    return html.Div(
        [
            dcc.Store(data=session_id2, id="session-id2"),
            html.Button("Get data", id="get-data-button2"),
            html.Div(id="output-1-2"),
            html.Div(id="output-2-2"),
        ]
    )


@callback(
    Output("output-1-2", "children"),
    Input("get-data-button2", "n_clicks"),
    Input("session-id2", "data"),
    prevent_initial_call=True,
)
def display_value_1(value, session_id):
    df = get_dataframe2(session_id)
    return html.Div(
        [
            "Output 1 - Button has been clicked {} times".format(value),
            html.Pre(df.to_csv()),
        ]
    )


@callback(
    Output("output-2-2", "children"),
    Input("get-data-button2", "n_clicks"),
    Input("session-id2", "data"),
    prevent_initial_call=True,
)
def display_value_2(value, session_id):
    df = get_dataframe2(session_id)
    return html.Div(
        [
            "Output 2 - Button has been clicked {} times".format(value),
            html.Pre(df.to_csv()),
        ]
    )
