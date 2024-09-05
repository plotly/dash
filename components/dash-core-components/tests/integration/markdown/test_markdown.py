import pytest
from dash import Dash, dcc, html, Input, Output
from dash.testing.wait import until


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
    app = Dash(__name__, eager_loading=is_eager)

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
    app = Dash(__name__, eager_loading=is_eager, assets_folder="../../assets")

    app.layout = html.Div(
        [
            dcc.Markdown("# h1 tag with inline MathJax: $E=mc^2$", mathjax=True),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("h1 svg")
    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_mkdw005_block_mathjax(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager, assets_folder="../../assets")

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
                id="md",
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#md svg")
    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_mkdw006_toggle_mathjax(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)

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
    app = Dash(__name__, eager_loading=is_eager)

    gravity = "$F=\\frac{Gm_1m_2}{r^2}$"

    app.layout = html.Div(
        [
            html.Button("Add Second MathJax", id="btn"),
            dcc.Markdown(
                f"""
                    # No Math Rendering Here! {gravity}
                """,
                id="md",
                mathjax=False,
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


def test_mkdw008_mathjax_visual(dash_dcc):
    app = Dash(__name__, assets_folder="../../assets")

    false = False

    # json
    fig = {
        "data": [
            {"x": [0, 1], "y": [0, 1.414], "name": "$E^2=m^2c^4+p^2c^2$"},
            {
                "x": [0, 1],
                "y": [1.4, 0.1],
                "type": "bar",
                "name": "$x=\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$",
            },
            {
                "type": "pie",
                "values": [1, 9],
                "labels": ["$\\frac{1}{10}=10\\%$", "$\\frac{9}{10}=90\\%$"],
                "domain": {"x": [0.3, 0.75], "y": [0.55, 1]},
            },
            {
                "type": "heatmap",
                "z": [[1, 2], [3, 4]],
                "xaxis": "x2",
                "yaxis": "y2",
                "colorbar": {"y": 0.225, "len": 0.45},
            },
        ],
        "layout": {
            "yaxis": {"domain": [0, 0.45], "title": {"text": "$y=\\sin{2 \\theta}$"}},
            "xaxis": {
                "domain": [0, 0.45],
                "title": {"text": "$x=\\int_0^a a^2+1$"},
                "tickvals": [0, 1],
                "ticktext": ["$\\frac{0}{100}$", "$\\frac{100}{100}$"],
            },
            "xaxis2": {"domain": [0.85, 1], "anchor": "y2"},
            "yaxis2": {
                "domain": [0, 0.45],
                "anchor": "x2",
                "title": {"text": "$(||01\\rangle+|10\\rangle)/\\sqrt2$"},
            },
            "height": 500,
            "width": 800,
            "margin": {"r": 250},
            "title": {
                "text": "$i\\hbar\\frac{d\\Psi}{dt}=-[V-\\frac{-\\hbar^2}{2m}\\nabla^2]\\Psi$"
            },
            "annotations": [
                {
                    "text": "$(top,left)$",
                    "showarrow": false,
                    "xref": "paper",
                    "yref": "paper",
                    "xanchor": "left",
                    "yanchor": "top",
                    "x": 0,
                    "y": 1,
                    "textangle": 10,
                    "bordercolor": "#0c0",
                    "borderpad": 3,
                    "bgcolor": "#dfd",
                },
                {
                    "text": "$(right,bottom)$",
                    "xref": "paper",
                    "yref": "paper",
                    "xanchor": "right",
                    "yanchor": "bottom",
                    "x": 0.2,
                    "y": 0.7,
                    "ax": -20,
                    "ay": -20,
                    "textangle": -30,
                    "bordercolor": "#0c0",
                    "borderpad": 3,
                    "bgcolor": "#dfd",
                    "opacity": 0.5,
                },
                {"text": "$not-visible$", "visible": false},
                {
                    "text": "$^{29}Si$",
                    "x": 0.7,
                    "y": 0.7,
                    "showarrow": false,
                    "xanchor": "right",
                    "yanchor": "top",
                },
                {
                    "text": "$^{17}O$",
                    "x": 0.7,
                    "y": 0.7,
                    "ax": 15,
                    "ay": -15,
                    "xanchor": "left",
                    "yanchor": "bottom",
                },
            ],
        },
    }

    app.layout = html.Div(
        children=[
            dcc.Markdown("# h1 tag with inline MathJax: $E=mc^2$", mathjax=True),
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
            dcc.Graph(mathjax=True, id="graph-with-math", figure=fig),
            dcc.Markdown("### No MathJax: Apple: $2, Orange: $3"),
            dcc.Graph(id="graph-without-math", figure=fig),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.find_element("h1 svg")
    dash_dcc.find_element("#graph-with-math svg")
    assert dash_dcc.driver.execute_script("return !!window.MathJax")

    dash_dcc.percy_snapshot("mkdw008 - markdown and graph with/without mathjax")

    assert dash_dcc.get_logs() == []


def test_mkdw009_target_blank_links(dash_dcc):

    app = Dash(__name__)

    app.layout = dcc.Markdown("[link](https://duckduckgo.com)", link_target="_blank")

    dash_dcc.start_server(app)

    dash_dcc.find_element("a").click()

    until(lambda: len(dash_dcc.driver.window_handles) == 2, timeout=1)


def test_mkdw010_mathjax_with_html(dash_dcc):

    app = Dash(__name__)

    CONTENT = [
        """
    <details>
        <summary>Topic</summary>
        Some details
    </details>

    $E = mc^2$
    """,
        """
    <p>Some paragraph</p>

    $E = mc^2$
    """,
        """
    <p>Some paragraph</p>
    $E = mc^2$
    """,
        """
    <p>Some paragraph</p> $E = mc^2$
    """,
        """
    <p>Some paragraph with $E = mc^2$ inline math</p>
    """,
    ]

    app.layout = html.Div(
        [dcc.Markdown(c, dangerously_allow_html=True, mathjax=True) for c in CONTENT]
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_element(".MathJax")
    assert len(dash_dcc.find_elements((".MathJax"))) == len(CONTENT)
