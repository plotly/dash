import dash
import dash_core_components as dcc
import dash_html_components as html


def test_mkdw001_img(dash_dcc):
    app = dash.Dash(__name__, eager_loading=True, assets_folder="../../assets")

    app.layout = html.Div(
        [
            html.Div("Markdown img"),
            dcc.Markdown(
                ['<img src="assets/image.png" />'], dangerously_allow_html=True
            ),
            html.Div("Markdown img - requires dangerously_allow_html"),
            dcc.Markdown(['<img src="assets/image.png" />']),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.percy_snapshot("mkdw001 - image display")

    assert dash_dcc.get_logs() == []


def test_mkdw002_dcclink(dash_dcc):
    app = dash.Dash(__name__, eager_loading=True, assets_folder="../../assets")

    app.layout = html.Div(
        [
            html.Div(["Markdown link"]),
            dcc.Markdown(["[Title](title_crumb)"]),
            html.Div(["Markdown dccLink"]),
            dcc.Markdown(
                ['<dccLink href="title_crumb" children="Title" />'],
                dangerously_allow_html=True,
            ),
            html.Div(["Markdown dccLink - explicit children"]),
            dcc.Markdown(
                [
                    """
            <dccLink href="title_crumb">
                Title
            </dccLink>
        """
                ],
                dangerously_allow_html=True,
            ),
            html.Div("Markdown dccLink = inlined"),
            dcc.Markdown(
                [
                    'This is an inlined <dccLink href="title_crumb" children="Title" /> with text on both sides'
                ],
                dangerously_allow_html=True,
            ),
            html.Div("Markdown dccLink - nested image"),
            dcc.Markdown(
                [
                    """
            <dccLink href="title_crumb">
                <img src="assets/image.png" />
            </dccLink>
        """
                ],
                dangerously_allow_html=True,
            ),
            html.Div("Markdown dccLink - nested markdown"),
            dcc.Markdown(
                [
                    """
            <dccLink href="title_crumb">
                <dccMarkdown children="## Title" />
            </dccLink>
        """
                ],
                dangerously_allow_html=True,
            ),
            html.Div("Markdown dccLink - nested markdown image"),
            dcc.Markdown(
                [
                    """
            <dccLink href="title_crumb">
                <dccMarkdown children="![Image](assets/image.png)" />
            </dccLink>
        """
                ],
                dangerously_allow_html=True,
            ),
            html.Div("Markdown dccLink - requires dangerously_allow_html"),
            dcc.Markdown(['<dccLink href="title_crumb" children="Title" />']),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.percy_snapshot("mkdw002 - markdowns display")

    assert dash_dcc.get_logs() == []
