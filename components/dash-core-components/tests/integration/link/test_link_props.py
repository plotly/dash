from multiprocessing import Lock

from dash import Dash, Input, Output, dcc, html


def test_lipr001_target(dash_dcc):
    # The `target` attribute is rendered on the anchor; links with a target
    # (other than _self) opt out of client-side navigation.
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Link("external", id="link1", href="/page-1", target="_blank"),
        ]
    )
    dash_dcc.start_server(app)

    link = dash_dcc.wait_for_element("#link1")
    assert link.get_attribute("target") == "_blank"

    assert dash_dcc.get_logs() == []


def test_lipr002_sanitizes_dangerous_href(dash_dcc):
    # A dangerous href is passed through clean_url, which rewrites disallowed
    # protocols to about:blank so the link can't execute script.
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Link("click me", id="link1", href="javascript:alert(1)"),
        ]
    )
    dash_dcc.start_server(app)

    link = dash_dcc.wait_for_element("#link1")
    assert link.get_attribute("href") == "about:blank"


def test_lipr003_loading_state(dash_dcc):
    # While a callback targeting the Link is in flight, the anchor carries
    # `data-dash-is-loading` (applied via LoadingElement).
    lock = Lock()

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            dcc.Link("Page 1", id="link1", href="/page-1"),
        ]
    )

    @app.callback(Output("link1", "children"), Input("btn", "n_clicks"))
    def update_children(n_clicks):
        with lock:
            return "Page 1"

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.wait_for_element('#link1[data-dash-is-loading="true"]')

    dash_dcc.wait_for_element('#link1:not([data-dash-is-loading="true"])')

    with lock:
        dash_dcc.wait_for_element("#btn").click()
        dash_dcc.wait_for_element('#link1[data-dash-is-loading="true"]')

    dash_dcc.wait_for_element('#link1:not([data-dash-is-loading="true"])')

    assert dash_dcc.get_logs() == []
