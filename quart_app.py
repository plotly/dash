from dash import Dash, html, Input, Output
from dash import dcc
from dash import backends

app = Dash(__name__, backend="quart")

app.layout = html.Div(
    [
        html.H2("Quart Server Factory Example"),
        html.Div("Type below to see async callback update."),
        dcc.Input(id="text", value="hello", autoComplete="off"),
        html.Div(id="echo"),
    ]
)


@app.callback(Output("echo", "children"), Input("text", "value"))
def update_echo(val):
    return f"You typed: {val}" if val else "Type something"


if __name__ == "__main__":
    app.run(debug=True)
