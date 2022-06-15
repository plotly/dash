import json
import itertools

from dash import Dash, html, dcc


def test_dada001_assets(dash_duo):
    app = Dash(__name__, assets_ignore=".*ignored.*")
    app.index_string = """<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%css%}
        </head>
        <body>
            <div id="tested"></div>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>"""

    app.layout = html.Div(
        [html.Div("Content", id="content"), dcc.Input(id="test")], id="layout"
    )

    dash_duo.start_server(app)

    assert (
        dash_duo.find_element("body").value_of_css_property("margin") == "0px"
    ), "margin is overloaded by assets css resource"

    assert (
        dash_duo.find_element("#content").value_of_css_property("padding") == "8px"
    ), "padding is overloaded by assets"

    tested = json.loads(dash_duo.wait_for_element("#tested").text)

    order = [
        "load_first",
        "load_after",
        "load_after1",
        "load_after10",
        "load_after11",
        "load_after2",
        "load_after3",
        "load_after4",
    ]

    assert order == tested, "the content and order is expected"


def test_dada002_external_files_init(dash_duo):
    js_files = [
        "https://www.google-analytics.com/analytics.js",
        {"src": "https://cdn.polyfill.io/v2/polyfill.min.js"},
        {
            "src": "https://cdnjs.cloudflare.com/ajax/libs/ramda/0.26.1/ramda.min.js",
            "integrity": "sha256-43x9r7YRdZpZqTjDT5E0Vfrxn1ajIZLyYWtfAXsargA=",
            "crossorigin": "anonymous",
        },
        {
            "src": "https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.11/lodash.min.js",
            "integrity": "sha256-7/yoZS3548fXSRXqc/xYzjsmuW3sFKzuvOCHd06Pmps=",
            "crossorigin": "anonymous",
        },
    ]

    css_files = [
        "https://codepen.io/chriddyp/pen/bWLwgP.css",
        {
            "href": "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
            "rel": "stylesheet",
            "integrity": "sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO",
            "crossorigin": "anonymous",
        },
    ]

    app = Dash(__name__, external_scripts=js_files, external_stylesheets=css_files)

    app.index_string = """<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%css%}
        </head>
        <body>
            <div id="tested"></div>
            <div id="ramda-test"></div>
            <button type="button" id="btn">Btn</button>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>"""

    app.layout = html.Div()

    dash_duo.start_server(app)

    js_urls = [x["src"] if isinstance(x, dict) else x for x in js_files]
    css_urls = [x["href"] if isinstance(x, dict) else x for x in css_files]

    for fmt, url in itertools.chain(
        (("//script[@src='{}']", x) for x in js_urls),
        (("//link[@href='{}']", x) for x in css_urls),
    ):
        dash_duo.find_element(fmt.format(url), attribute="XPATH")

    assert (
        dash_duo.find_element("#btn").value_of_css_property("height") == "18px"
    ), "Ensure the button style was overloaded by reset (set to 38px in codepen)"

    # ensure ramda was loaded before the assets so they can use it.
    assert dash_duo.find_element("#ramda-test").text == "Hello World"
