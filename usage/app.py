from dash import Dash, html, dcc, Output, Input
import dash
import random


app = Dash(__name__, use_pages=True)

dash.register_page("another_home", layout=html.Div("We're home!"), path="/")
dash.register_page(
    "very_important", layout=html.Div("Don't miss it!"), path="/important", order=0
)

app.layout = html.Div(
    [
        html.H1("App Frame"),
        html.Button("goto", id="goto"),
        html.Div(
            [
                html.Div(
                    dcc.Link(
                        f"{page['name']} - {page['path']}", href=page["relative_path"]
                    )
                )
                for page in dash.page_registry.values()
                if page["module"] != "pages.not_found_404"
            ]
        ),
        dash.page_container,
        # example of using the url for doing something other than serving the layout to dash.page_container
        dcc.Location(id="url", refresh=False),
        html.Div(id="custom_output", style={"marginTop": 50}),
    ]
)


@app.callback(Output("custom_output", "children"), Input("url", "pathname"))
def example_custom_output(pathname):
    return f"custom function or output for url {pathname}"


@app.callback(Output("url", "pathname"), Input("goto", "n_clicks"), prevent_initial_call=True)
def goto(n):
    x=random.randrange(1,10)
    return f"/goto-{x}-and-{x+2}-data"


if __name__ == "__main__":
    app.run_server(debug=True)
