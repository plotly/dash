import time
import dash
from dash import html, dcc, Input, Output

dash.register_page(__name__)

app = dash.get_app()

layout = html.Div(
    [
        html.Div([html.P(id="paragraph_id", children=["Button not clicked"])]),
        html.Button(id="button_id", children="Run Job!", n_clicks=0),
    ]
)


@app.long_callback(
    output=Output("paragraph_id", "children"),
    inputs=Input("button_id", "n_clicks"),
    running=[
        (Output("button_id", "disabled"), True, False),
    ],
    prevent_initial_call=True,
)
def callback(n_clicks):
    time.sleep(5.0)
    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
