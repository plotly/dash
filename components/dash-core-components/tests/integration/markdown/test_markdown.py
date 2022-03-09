import pytest
from dash import Dash, dcc, html, Input, Output


def test_mkdw001_img(dash_dcc):
    app = Dash(__name__, eager_loading=True, assets_folder="../../assets")

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
    app = Dash(__name__, eager_loading=True, assets_folder="../../assets")

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
    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_mkdw003_without_mathjax(dash_dcc, is_eager):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Markdown("# No MathJax: Apple: $2, Orange: $3"),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("h1", "No MathJax: Apple: $2, Orange: $3")
    assert not dash_dcc.driver.execute_script("return !!window.MathJax")
    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_mkdw004_inline_mathjax(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=False, assets_folder="../../assets")

    app.layout = html.Div(
        [
            dcc.Markdown("# h1 tag with inline MathJax: $E=mc^2$", mathjax=True),
        ]
    )

    dash_dcc.start_server(app)
    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_mkdw005_block_mathjax(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=False, assets_folder="../../assets")

    app.layout = html.Div(
        [
            dcc.Markdown(
                """
                    ## h2 tag with MathJax block:
                    $$
                    \\frac{1}{(\\sqrt{\\phi \\sqrt{5}}-\\phi) e^{\\frac25 \\pi}} =
                    1+\\frac{e^{-2\\pi}} {1+\\frac{e^{-4\\pi}} {1+\\frac{e^{-6\\pi}}
                    {1+\\frac{e^{-8\\pi}} {1+\\ldots} } } }
                    $$
                    ## Next line.
                """,
                mathjax=True,
            ),
        ]
    )

    dash_dcc.start_server(app)
    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_mkdw006_toggle_mathjax(dash_dcc, is_eager):
    app = Dash(__name__)

    gravity = "$F=\\frac{Gm_1m_2}{r^2}$"

    app.layout = html.Div(
        [
            html.Button("Toggle MathJax", id="btn"),
            dcc.Markdown(
                f"""
                    # Test MathJax Toggling {gravity}
                """,
                id="md",
            ),
        ]
    )

    @app.callback(
        Output("md", "mathjax"), Input("btn", "n_clicks"), prevent_initial_call=True
    )
    def toggle(n):
        return (n or 0) % 2 != 0

    dash_dcc.start_server(app)

    # Initial state: no MathJax loaded or rendered, unformatted text is shown
    dash_dcc.wait_for_contains_text("#md", gravity)
    dash_dcc.wait_for_no_elements("#md svg")
    assert not dash_dcc.driver.execute_script("return !!window.MathJax")

    btn = dash_dcc.find_element("#btn")
    btn.click()

    # One click: MathJax is rendered, unformatted text is gone

    dash_dcc.wait_for_element("#md svg")
    assert gravity not in dash_dcc._get_element("#md").text
    assert dash_dcc.driver.execute_script("return !!window.MathJax")

    btn.click()

    # Second click: Back to initial state except that MathJax library is still loaded
    dash_dcc.wait_for_contains_text("#md", gravity)
    dash_dcc.wait_for_no_elements("#md svg")
    assert dash_dcc.driver.execute_script("return !!window.MathJax")


@pytest.mark.parametrize("is_eager", [True, False])
def test_mkdw007_load_mathjax(dash_dcc, is_eager):
    app = Dash(__name__)

    gravity = "$F=\\frac{Gm_1m_2}{r^2}$"

    app.layout = html.Div(
        [
            html.Button("Add Second MathJax", id="btn"),
            dcc.Markdown(
                f"""
                # No Math Rendering Here! {gravity}
            """,
                id="md",
            ),
            html.Div("initial", id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"), Input("btn", "n_clicks"), prevent_initial_call=True
    )
    def add_math(n):
        return dcc.Markdown(f"# Math!\n{gravity}", id="md2", mathjax=True)

    dash_dcc.start_server(app)

    # Initial state: no MathJax loaded or rendered, unformatted text is shown
    dash_dcc.wait_for_contains_text("#md", gravity)
    dash_dcc.wait_for_no_elements("#md svg")
    assert not dash_dcc.driver.execute_script("return !!window.MathJax")

    btn = dash_dcc.find_element("#btn")
    btn.click()

    # One click: MathJax is loaded and rendered on the second, unformatted text is gone

    dash_dcc.wait_for_element("#md2 svg")
    assert gravity not in dash_dcc._get_element("#md2").text
    assert dash_dcc.driver.execute_script("return !!window.MathJax")
