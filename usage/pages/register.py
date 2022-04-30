import dash
from dash import Dash, dcc, html, Input, Output, State

dash.register_page(
    __name__,
)
app = dash.get_app()
# This page is invoked by:
#
#   http://localhost:8050/register?email=harrysmall%40gmail.com


def layout(email=None):
    store_email = dcc.Store(id="email", data=email)
    heading = html.H2(f"Register {email}?")
    btn = html.Button("Click to register", id="btn")
    confirm = html.H2(id="confirm")
    hint = html.Small(
        "try entering an email address in the url eg: http://localhost:8050/register?email=harrysmall%40gmail.com"
    )

    return html.Div([heading, btn, confirm, html.Br(), hint, store_email])


@app.callback(
    Output("confirm", "children"),
    Input("btn", "n_clicks"),
    State("email", "data"),
    prevent_initial_call=True,
)
def register_cb(clicks, email):
    if clicks:
        return f"User {email} has been registered"
    else:
        return None
