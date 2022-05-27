import dash
from dash import dcc, html, Input, Output, State, callback, ctx


layout = html.Div(
    [
        "Enter a product code",
        dcc.Input(id="product", type="number", value=200),
        html.Button("submit", id="btn", n_clicks=0),
    ]
)


@callback(
    Output("url-main", "href"),
    Input("btn", "n_clicks"),
    State("product", "value"),
    prevent_initial_call=True,
)
def update_url(n, prodcode):
    print(ctx.triggered_id)
    print(n, prodcode)
    if n == 0:
        return dash.no_update
    prodcode = prodcode if prodcode else "none"
    if prodcode and prodcode < 1000:
        return f"/frozen?prodcode={prodcode}"
    else:
        return f"/produce?prodcode={prodcode}"
