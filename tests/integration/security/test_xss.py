from dash import Dash, html, dcc


def test_xss001_banned_protocols(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            dcc.Link("dcc-link", href="javascript:alert(1)", id="dcc-link"),
            html.Br(),
            html.A(
                "html.A", href='javascr\nipt:alert(1);console.log("xss");', id="html-A"
            ),
            html.Br(),
            html.Form(
                [
                    html.Button(
                        "form-action",
                        formAction="javascript:alert('form-action')",
                        id="button-form-action",
                    ),
                    html.Button("submit", role="submit"),
                ],
                action='javascript:alert(1);console.log("xss");',
                id="form",
            ),
            html.Iframe(src='javascript:alert("iframe")', id="iframe-src"),
            html.ObjectEl(data='javascript:alert("data-object")', id="object-data"),
            html.Embed(src='javascript:alert("embed")', id="embed-src"),
        ]
    )

    dash_duo.start_server(app)

    for element_id, prop in (
        ("#dcc-link", "href"),
        ("#html-A", "href"),
        ("#iframe-src", "src"),
        ("#object-data", "data"),
        ("#embed-src", "src"),
        ("#button-form-action", "formAction"),
    ):

        element = dash_duo.find_element(element_id)
        assert (
            element.get_attribute(prop) == "about:blank"
        ), f"Failed prop: {element_id}.{prop}"


def test_xss002_blank_href(dash_duo):
    app = Dash()

    app.layout = html.Div(dcc.Link("dcc-link", href="", id="dcc-link-no-href"))

    dash_duo.start_server(app)

    element = dash_duo.find_element("#dcc-link-no-href")
    assert element.get_attribute("href") is None

    assert dash_duo.get_logs() == []
