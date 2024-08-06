from dash import Dash, html, dcc


def test_xss001_banned_protocols(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            dcc.Link("dcc-link", href="javascript:alert(1)", id="dcc-link"),
            html.Br(),
            html.A(
                "html.A",
                href='javascr\n\nipt:alert(1);console.log("xss");',
                id="html-A",
            ),
            html.A(
                "html.A.escape",
                id="html-A-escape",
                href="""javascript\x09\x0a:alert(1)""",
            ),
            html.A(
                "html.A.encoded",
                id="html-A-encoded",
                href="&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116&#0000058&#0000097&#0000108&#0000101&#0000114&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041",
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
        ("#html-A-escape", "href"),
        ("#html-A-encoded", "href"),
        ("#iframe-src", "src"),
        ("#object-data", "data"),
        ("#embed-src", "src"),
        ("#button-form-action", "formAction"),
    ):

        element = dash_duo.find_element(element_id)
        prop_value = element.get_attribute(prop)
        assert (
            prop_value == "about:blank"
        ), f"Failed prop: {element_id}.{prop} = {prop_value}"


def test_xss002_blank_href(dash_duo):
    app = Dash()

    app.layout = html.Div(dcc.Link("dcc-link", href="", id="dcc-link-no-href"))

    dash_duo.start_server(app)

    element = dash_duo.find_element("#dcc-link-no-href")
    assert element.get_attribute("href") is None

    assert dash_duo.get_logs() == []


def test_xss003_data_allowed(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            html.Img(
                id="image",
                src="data:image/png;base64,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",
            )
        ]
    )

    dash_duo.start_server(app)
    element = dash_duo.find_element("#image")
    assert element.get_attribute("src") != "about:blank"
    assert dash_duo.get_logs() == []
