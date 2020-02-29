import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import logging
import os


logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = dash.Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/dZVMbK.css"]
)
app.config["suppress_callback_exceptions"] = True

server = app.server

apps = {
    filename.replace(".py", "").replace("app_", ""): getattr(
        getattr(
            __import__(".".join(["tests", "integration", filename.replace(".py", "")])),
            "integration",
        ),
        filename.replace(".py", ""),
    )
    for filename in os.listdir(os.path.join("tests", "integration"))
    if filename.startswith("app_") and filename.endswith(".py")
}


app.layout = html.Div(
    children=[
        dcc.Location(id="location"),
        html.Div(id="container"),
        html.Div(style={"display": "none"}, children=dash_table.DataTable(id="hidden")),
    ]
)


@app.callback(Output("container", "children"), [Input("location", "pathname")])
def display_app(pathname):
    if pathname == "/" or pathname is None:
        return html.Div(
            className="container",
            children=[
                html.H1("Dash Table Review App"),
                html.Ol(
                    [
                        html.Li(
                            dcc.Link(
                                name.replace("app_", "").replace("_", " "),
                                href="/{}".format(
                                    name.replace("app_", "").replace("_", "-")
                                ),
                            )
                        )
                        for name in apps
                    ]
                ),
            ],
        )

    app_name = pathname.replace("/", "").replace("-", "_")
    if app_name in apps:
        return html.Div(
            [
                html.H3(app_name.replace("-", " ")),
                html.Div(id="waitfor"),
                html.Div(apps[app_name].layout()),
            ]
        )
    else:
        return """
            App not found.
            You supplied "{}" and these are the apps that exist:
            {}
        """.format(
            app_name, list(apps.keys())
        )


app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

if __name__ == "__main__":
    app.run_server(debug=True)
