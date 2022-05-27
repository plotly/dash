import dash
from dash import Dash, dcc, html, Input, Output
from pages import frozen, home, produce
from urllib.parse import parse_qs

app = Dash(__name__, suppress_callback_exceptions=True)


def _parse_query_string(search):
    if search and len(search) > 0 and search[0] == "?":
        search = search[1:]
    else:
        return {}

    parsed_qs = {}
    for (k, v) in parse_qs(search).items():
        v = v[0] if len(v) == 1 else v
        parsed_qs[k] = v
    return parsed_qs


app.layout = html.Div(
    [
        html.Div("Navigate with dcc.Link"),
        dcc.Link("home  ", href="/"),
        dcc.Link("frozen  ", href="frozen"),
        dcc.Link("produce  ", href="produce"),


        dcc.Location("url-main", refresh="callback-nav"),
        html.Div(id="app-content", style={"marginTop":10}),

    ]
)


@app.callback(
    Output("app-content", "children"),
    Input("url-main", "pathname"),
    Input("url-main", "search"),
)
def index(path, search):
    query_parameters = _parse_query_string(search)

    if path == "/":
        return home.layout
    if path == "/frozen":
        return frozen.layout(**query_parameters)
    if path == "/produce":
        return produce.layout(**query_parameters)
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(debug=True)
