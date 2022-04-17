# example of query strings. Try entering ?velocity=20 at the end of the url.
import dash

dash.register_page(__name__, path="/dashboard")


def layout(velocity=None, **other_unknown_query_strings):
    return dash.html.Div([dash.dcc.Input(id="velocity", value=velocity)])
