import pytest
from dash import Dash, dcc, html, Input, Output
from dash.testing.wait import until


GRAVITY = "$F=\\frac{Gm_1m_2}{r^2}$"

BLOCK_MATH = """
    ## h2 tag with MathJax block:
    $$
    \\frac{1}{(\\sqrt{\\phi \\sqrt{5}}-\\phi) e^{\\frac25 \\pi}} =
    1+\\frac{e^{-2\\pi}} {1+\\frac{e^{-4\\pi}} {1+\\frac{e^{-6\\pi}}
    {1+\\frac{e^{-8\\pi}} {1+\\ldots} } } }
    $$
    ## Next line.
"""


def test_mkdw001_img(dash_dcc):
    app = Dash(__name__, eager_loading=True, assets_folder="../../assets")

    app.layout = html.Div(
        [
            html.Div("Markdown img"),
            dcc.Markdown(
                ['<img src="assets/image.png" />'],
                dangerously_allow_html=True,
                id="img_html",
            ),
            html.Div("Markdown img - requires dangerously_allow_html"),
            dcc.Markdown(['<img src="assets/image.png" />'], id="img_no_html"),
        ]
    )

    dash_dcc.start_server(app)

    # With dangerously_allow_html the raw <img> renders as a real image.
    img = dash_dcc.wait_for_element("#img_html img")
    assert img.get_attribute("src").endswith("assets/image.png")

    # Without it, the raw HTML is inert - no <img> element is created.
    dash_dcc.wait_for_no_elements("#img_no_html img")

    dash_dcc.percy_snapshot("mkdw001 - image display")

    assert dash_dcc.get_logs() == []


def test_mkdw002_dcclink(dash_dcc):
    app = Dash(__name__, eager_loading=True, assets_folder="../../assets")

    app.layout = html.Div(
        [
            html.Div(["Markdown link"]),
            dcc.Markdown(["[Title](title_crumb)"], id="md_link"),
            html.Div(["Markdown dccLink"]),
            dcc.Markdown(
                ['<dccLink href="title_crumb" children="Title" />'],
                dangerously_allow_html=True,
                id="dcclink_attr",
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
                id="dcclink_explicit",
            ),
            html.Div("Markdown dccLink = inlined"),
            dcc.Markdown(
                [
                    'This is an inlined <dccLink href="title_crumb" children="Title" /> with text on both sides'
                ],
                dangerously_allow_html=True,
                id="dcclink_inline",
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
                id="dcclink_nested_img",
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
                id="dcclink_nested_md",
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
                id="dcclink_nested_md_img",
            ),
            html.Div("Markdown dccLink - requires dangerously_allow_html"),
            dcc.Markdown(
                ['<dccLink href="title_crumb" children="Title" />'],
                id="dcclink_no_html",
            ),
        ]
    )

    dash_dcc.start_server(app)

    # Baseline: a plain Markdown link renders an anchor with the link text.
    dash_dcc.wait_for_text_to_equal("#md_link a", "Title")

    # The regression from https://github.com/plotly/dash/issues/3951:
    # a self-closing dccLink whose text is supplied via the `children`
    # attribute must render "Title", NOT the href. When react-jsx-parser
    # clobbered the attribute, dcc.Link fell back to rendering the href.
    dash_dcc.wait_for_text_to_equal("#dcclink_attr a", "Title")
    assert (
        dash_dcc.find_element("#dcclink_attr a")
        .get_attribute("href")
        .endswith("title_crumb")
    )

    # The nested-content form renders identically.
    dash_dcc.wait_for_text_to_equal("#dcclink_explicit a", "Title")
    assert (
        dash_dcc.find_element("#dcclink_explicit a")
        .get_attribute("href")
        .endswith("title_crumb")
    )

    # An inlined dccLink carries the children text on the anchor itself,
    # with the surrounding prose on the parent element.
    dash_dcc.wait_for_text_to_equal("#dcclink_inline a", "Title")
    assert "with text on both sides" in dash_dcc.find_element("#dcclink_inline").text

    # A raw <img> nested inside the link renders an <img>, not href text.
    dash_dcc.wait_for_element("#dcclink_nested_img a img")

    # A nested dccMarkdown renders its markdown (an <h2>) inside the link.
    dash_dcc.wait_for_text_to_equal("#dcclink_nested_md a h2", "Title")

    # A nested dccMarkdown image renders an <img> inside the link.
    dash_dcc.wait_for_element("#dcclink_nested_md_img a img")

    # Without dangerously_allow_html the tag is inert: no anchor is rendered.
    dash_dcc.wait_for_no_elements("#dcclink_no_html a")

    assert dash_dcc.get_logs() == []


def test_mkdw003_without_mathjax(dash_dcc):
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


@pytest.mark.parametrize(
    "markdown",
    [
        "# h1 tag with inline MathJax: $E=mc^2$",
        BLOCK_MATH,
    ],
    ids=["inline", "block"],
)
def test_mkdw004_mathjax_renders(dash_dcc, markdown):
    # Both inline ($...$) and block ($$...$$) math render to an <svg>.
    app = Dash(__name__, assets_folder="../../assets")

    app.layout = html.Div([dcc.Markdown(markdown, mathjax=True, id="md")])

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#md svg")
    assert dash_dcc.get_logs() == []


def _toggle_mathjax_setup(app):
    # Flip an existing Markdown's `mathjax` prop on via callback.
    app.layout = html.Div(
        [
            html.Button("Toggle MathJax", id="btn"),
            dcc.Markdown(f"# Test MathJax {GRAVITY}", id="md"),
        ]
    )

    @app.callback(
        Output("md", "mathjax"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle(n):
        return (n or 0) % 2 != 0

    return "#md"


def _add_mathjax_setup(app):
    # Inject a brand-new mathjax=True Markdown via callback.
    app.layout = html.Div(
        [
            html.Button("Add MathJax", id="btn"),
            dcc.Markdown(f"# No Math Here! {GRAVITY}", id="md", mathjax=False),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def add(n):
        return dcc.Markdown(f"# Math!\n{GRAVITY}", id="md2", mathjax=True)

    return "#md2"


@pytest.mark.parametrize("is_eager", [True, False])
@pytest.mark.parametrize("setup", [_toggle_mathjax_setup, _add_mathjax_setup])
def test_mkdw006_mathjax_loads_on_demand(dash_dcc, is_eager, setup):
    # MathJax isn't loaded until a mathjax=True Markdown renders - whether that
    # happens by toggling the prop or by injecting a new component.
    app = Dash(__name__, eager_loading=is_eager)

    rendered = setup(app)

    dash_dcc.start_server(app)

    # Initial state: no MathJax loaded or rendered, raw delimiters are shown.
    dash_dcc.wait_for_contains_text("#md", GRAVITY)
    dash_dcc.wait_for_no_elements("#md svg")
    assert not dash_dcc.driver.execute_script("return !!window.MathJax")

    dash_dcc.find_element("#btn").click()

    # After the click: MathJax is loaded and the math renders as <svg>.
    dash_dcc.wait_for_element(f"{rendered} svg")
    assert GRAVITY not in dash_dcc._get_element(rendered).text
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
            dcc.Markdown(BLOCK_MATH, mathjax=True),
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


def test_mkdw011_dedent(dash_dcc):
    app = Dash(__name__)

    # Every line shares a 4-space indent. With dedent it becomes a heading;
    # without dedent the indent makes it an indented code block instead.
    indented = "    # Indented heading\n    with body text\n"

    app.layout = html.Div(
        [
            dcc.Markdown(indented, dedent=True, id="dedent_on"),
            dcc.Markdown(indented, dedent=False, id="dedent_off"),
        ]
    )

    dash_dcc.start_server(app)

    # dedent=True strips the common indent, so the line renders as a heading.
    dash_dcc.wait_for_text_to_equal("#dedent_on h1", "Indented heading")

    # dedent=False keeps the indent, so CommonMark renders a code block and
    # there is no heading.
    dash_dcc.wait_for_element("#dedent_off pre code")
    dash_dcc.wait_for_no_elements("#dedent_off h1")

    assert dash_dcc.get_logs() == []


def test_mkdw012_highlight_config_theme(dash_dcc):
    app = Dash(__name__)

    code = "```python\nprint('hello, world!')\n```"

    app.layout = html.Div(
        [
            dcc.Markdown(code, highlight_config={"theme": "dark"}, id="theme_dark"),
            dcc.Markdown(code, highlight_config={"theme": "light"}, id="theme_light"),
        ]
    )

    dash_dcc.start_server(app)

    # The dark theme adds the `hljs-dark` class to the container; light does not.
    dash_dcc.wait_for_element("#theme_dark pre code")
    assert "hljs-dark" in dash_dcc.find_element("#theme_dark").get_attribute("class")
    assert "hljs-dark" not in (
        dash_dcc.find_element("#theme_light").get_attribute("class") or ""
    )

    assert dash_dcc.get_logs() == []


def test_mkdw013_classname_and_style(dash_dcc):
    app = Dash(__name__)

    app.layout = dcc.Markdown(
        "Styled container",
        id="styled",
        className="my-markdown",
        style={"color": "rgb(1, 2, 3)"},
    )

    dash_dcc.start_server(app)

    container = dash_dcc.wait_for_element("#styled")
    assert "my-markdown" in container.get_attribute("class")
    # The inline style prop is applied to the container (the browser may
    # report the colour as rgb or rgba).
    assert "1, 2, 3" in container.value_of_css_property("color")

    # A plain string must render as a paragraph.
    dash_dcc.wait_for_text_to_equal("#styled p", "Styled container")
    dash_dcc.wait_for_no_elements("#styled pre")

    assert dash_dcc.get_logs() == []


def test_mkdw014_reuses_existing_mathjax(dash_dcc):
    # dcc shares a single global `window.MathJax`: whichever of dcc.Graph,
    # dcc.Markdown, or a user script loads it first wins, and everything else
    # (including plotly.js) reuses it. This locks in that dcc.Markdown respects
    # a pre-existing `window.MathJax` instead of loading/overwriting its own.
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("Add markdown", id="btn"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"), Input("btn", "n_clicks"), prevent_initial_call=True
    )
    def add(n):
        return dcc.Markdown("Inline $E=mc^2$ math", mathjax=True, id="md")

    dash_dcc.start_server(app)

    # Simulate MathJax already present on the page (as dcc.Graph, plotly, or a
    # user script would leave it) before any Markdown renders.
    dash_dcc.driver.execute_script(
        """
        window.MathJax = {
            _sentinel: 'preloaded',
            startup: {},
            config: {startup: {}},
            typeset: function (els) {
                (els || []).forEach(function (el) {
                    el.setAttribute('data-typeset', 'preloaded');
                });
            }
        };
        """
    )

    dash_dcc.find_element("#btn").click()

    # The math was typeset by the pre-existing MathJax (our sentinel)...
    dash_dcc.wait_for_element("#md [data-typeset='preloaded']")
    # ...and dcc did not replace the global with its own bundled copy.
    assert (
        dash_dcc.driver.execute_script(
            "return window.MathJax && window.MathJax._sentinel"
        )
        == "preloaded"
    )

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize(
    "tag, markup",
    [
        # <script> is an XSS vector the old react-jsx-parser also blacklisted.
        ("script", "before <script>window.__stripped = true;</script> after"),
        # <style> never rendered under the old implementation; we keep it inert
        # so styles don't silently start applying in a minor release.
        ("style", "before <style>body{display:none}</style> after"),
    ],
)
def test_mkdw016_strips_inert_tags(dash_dcc, tag, markup):
    # Even with dangerously_allow_html, these tags are removed from the tree.
    app = Dash(__name__)

    app.layout = html.Div(dcc.Markdown(markup, dangerously_allow_html=True, id="md"))

    dash_dcc.start_server(app)

    # Sibling content still renders - we skip the tag, we don't drop everything.
    dash_dcc.wait_for_contains_text("#md", "before")
    dash_dcc.wait_for_contains_text("#md", "after")
    # The tag itself never makes it into the DOM, so it stays inert.
    dash_dcc.wait_for_no_elements(f"#md {tag}")
    # In particular, a <script> body never executes.
    assert dash_dcc.driver.execute_script("return window.__stripped") is None

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize(
    "markdown",
    ["Prices: &#36;5 and &#36;10", "Prices: \\$5 and \\$10"],
    ids=["entity", "escaped"],
)
def test_mkdw017_literal_dollar_is_not_math(dash_dcc, markdown):
    # `&#36;` and `\$` are literal dollars, not math delimiters - even with
    # mathjax on, they must not be consumed into a rendered expression.
    app = Dash(__name__, assets_folder="../../assets")

    app.layout = html.Div([dcc.Markdown(markdown, mathjax=True, id="md")])

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#md", "Prices: $5 and $10")
    # Nothing was treated as math, so no expression is rendered.
    dash_dcc.wait_for_no_elements("#md .MathJax")

    assert dash_dcc.get_logs() == []
