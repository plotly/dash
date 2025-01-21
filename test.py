from types import SimpleNamespace

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import html, Dash, dcc, Input, Output, no_update, callback, dash_table


app = Dash()

app.layout = html.Div(
        [
            dbc.Alert(id="alert", is_open=False, duration=4000),
            dcc.DatePickerRange(
                id="date_picker",
                start_date="2021-01-01",
                end_date="2021-01-31",
            ),
            dcc.Graph(id="figcontainer"),
            dash_table.DataTable(id="table"),
        ]
    )


@callback(
    Output(component_id="figcontainer", component_property="figure"),
    Output(component_id="table", component_property="data"),
    Output(component_id="alert", component_property="is_open"),
    Output(component_id="alert", component_property="children"),
    Input(component_id="date_picker", component_property="start_date"),
    Input(component_id="date_picker", component_property="end_date"),
)
def update_graph(start, end):
    df = get_bookings_in_interval(start, end)
    # if there is no data, keep previous states and use alert
    if type(df) is AssertionError:
        return no_update, no_update, True, df

    fig = go.Figure()

    return (
        fig.to_dict(),
        {},
        no_update,
        no_update,
    )

mock_response = SimpleNamespace(
    status_code=404,
)

# either returns a df or an AssertionError
def get_bookings_in_interval(start, end):
    df = None
    try:
        data = mock_response
        assert data.status_code == 200, "Failed to fetch bookings"
        parsed_data = dict(data.json())
        assert len(parsed_data["bookings"]) > 0, "No items in Response"
        # do something

    except AssertionError as e:
        print(e)
        return e

    return data


if __name__ == '__main__':
    app.run(debug=True)