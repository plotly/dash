from dash import html, dcc, callback, Input, Output

import dash

dash.register_page(__name__)

layout = (html.Button("Add a Page Button", id="button"), html.Div(id="content"))


@callback(
    Output("content", "children"),
    Input("button", "n_clicks"),
    prevent_initial_call=True,
)
def update_output_div(n_clicks):

    dash.register_page(
        "callback_page",
        path=f"/callback-page/{n_clicks}",
        redirect_from=["/callback-page"],
        layout=html.Div(["Callback Page"]),
    )

    return f"New page created:  redirect_from= /callback-page   path= /callback-page/{n_clicks}"
