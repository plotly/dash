from dash import Dash, html, dcc


def test_inline_props(dash_dcc):
    app = Dash(__name__)

    options = ["one", "two", "three"]
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.H2(f"Inline: {inline}"),
                    dcc.RadioItems(options=options, inline=inline),
                    dcc.Checklist(options=options, inline=inline),
                ]
            )
            for inline in [True, False]
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.percy_snapshot("RadioItems/Checklist-inline")
