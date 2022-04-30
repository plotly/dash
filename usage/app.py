from dash import Dash, html, dcc, Output, Input
import dash
import flask
from dash.long_callback import DiskcacheLongCallbackManager


## Diskcache
import diskcache

cache_lc = diskcache.Cache("./cache_lc")
long_callback_manager = DiskcacheLongCallbackManager(cache_lc)

# Thi is the css from the cash example in the docs.  It's not compatible with long_callback
# external_stylesheets = [
#     # Dash CSS
#     "https://codepen.io/chriddyp/pen/bWLwgP.css",
#     # Loading screen CSS
#     "https://codepen.io/chriddyp/pen/brPBPO.css",
# ]

server = flask.Flask("my_server")
app = Dash(
    __name__, use_pages=True, server=False, long_callback_manager=long_callback_manager
)
app.init_app(server)


dash.register_page("another_home", layout=html.Div("We're home!"), path="/")
dash.register_page(
    "very_important", layout=html.Div("Don't miss it!"), path="/important", order=0
)

app.layout = html.Div(
    [
        html.H1("App Frame"),
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
        dcc.Location(id="url", refresh=True),
        html.Div(id="custom_output", style={"marginTop": 50}),
    ]
)


@app.callback(Output("custom_output", "children"), Input("url", "pathname"))
def example_custom_output(pathname):
    return f"custom function or output for url {pathname}"


if __name__ == "__main__":
    app.run_server(debug=True)
