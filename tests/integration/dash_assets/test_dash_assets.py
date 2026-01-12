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


def test_dada003_external_resources_with_attributes(dash_duo):
    """Test that attributes field works for external scripts and stylesheets"""
    app = Dash(__name__)

    # Test scripts with type="module" and other attributes
    app.scripts.append_script(
        {
            "external_url": "https://cdn.example.com/module-script.js",
            "attributes": {"type": "module"},
            "external_only": True,
        }
    )

    app.scripts.append_script(
        {
            "external_url": "https://cdn.example.com/async-script.js",
            "attributes": {"async": "true", "data-test": "custom"},
            "external_only": True,
        }
    )

    # Test CSS with custom attributes
    app.css.append_css(
        {
            "external_url": "https://cdn.example.com/print-styles.css",
            "attributes": {"media": "print"},
            "external_only": True,
        }
    )

    app.layout = html.Div("Test Layout", id="content")

    dash_duo.start_server(app)

    # Verify script with type="module" is rendered correctly
    module_script = dash_duo.find_element(
        "//script[@src='https://cdn.example.com/module-script.js' and @type='module']",
        attribute="XPATH",
    )
    assert (
        module_script is not None
    ), "Module script should be present with type='module'"

    # Verify script with async and custom data attribute
    async_script = dash_duo.find_element(
        "//script[@src='https://cdn.example.com/async-script.js' and @async='true' and @data-test='custom']",
        attribute="XPATH",
    )
    assert (
        async_script is not None
    ), "Async script should be present with custom attributes"

    # Verify CSS with media attribute
    print_css = dash_duo.find_element(
        "//link[@href='https://cdn.example.com/print-styles.css' and @media='print']",
        attribute="XPATH",
    )
    assert print_css is not None, "Print CSS should be present with media='print'"


def test_dada004_external_scripts_init_with_attributes(dash_duo):
    """Test that attributes work when passed via external_scripts in Dash constructor"""
    js_files = [
        "https://cdn.example.com/regular-script.js",
        {"src": "https://cdn.example.com/es-module.js", "type": "module"},
        {
            "src": "https://cdn.example.com/integrity-script.js",
            "integrity": "sha256-test123",
            "crossorigin": "anonymous",
        },
    ]

    css_files = [
        "https://cdn.example.com/regular-styles.css",
        {
            "href": "https://cdn.example.com/dark-theme.css",
            "media": "(prefers-color-scheme: dark)",
        },
    ]

    app = Dash(__name__, external_scripts=js_files, external_stylesheets=css_files)
    app.layout = html.Div("Test", id="content")

    dash_duo.start_server(app)

    # Verify regular script (string format)
    dash_duo.find_element(
        "//script[@src='https://cdn.example.com/regular-script.js']", attribute="XPATH"
    )

    # Verify ES module script
    module_script = dash_duo.find_element(
        "//script[@src='https://cdn.example.com/es-module.js' and @type='module']",
        attribute="XPATH",
    )
    assert module_script is not None

    # Verify script with integrity and crossorigin
    integrity_script = dash_duo.find_element(
        "//script[@src='https://cdn.example.com/integrity-script.js' and @integrity='sha256-test123' and @crossorigin='anonymous']",
        attribute="XPATH",
    )
    assert integrity_script is not None

    # Verify regular CSS
    dash_duo.find_element(
        "//link[@href='https://cdn.example.com/regular-styles.css']", attribute="XPATH"
    )

    # Verify CSS with media query
    dark_css = dash_duo.find_element(
        "//link[@href='https://cdn.example.com/dark-theme.css' and @media='(prefers-color-scheme: dark)']",
        attribute="XPATH",
    )
    assert dark_css is not None
