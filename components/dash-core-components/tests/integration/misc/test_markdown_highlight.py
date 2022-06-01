# -*- coding: utf-8 -*-

from dash import Dash, Input, Output, dcc, html


md_text = """```python
import dash
print('hello, world!')
```"""


def test_msmh001_no_window_variable(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(dcc.Markdown(md_text))
    dash_dcc.start_server(app)

    dash_dcc.wait_for_element("code")

    window_hljs = dash_dcc.driver.execute_script("return window.hljs")
    assert window_hljs is None

    assert dash_dcc.get_logs() == []


def test_msmh002_window_override(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("Click", id="md-trigger"), html.Div(id="md-container")]
    )

    # we can't run the script below until after the page has loaded,
    # so we need to trigger a rerender of the markdown component
    @app.callback(Output("md-container", "children"), [Input("md-trigger", "n_clicks")])
    def trigger_md_rerender(nclicks):
        if nclicks is not None and nclicks > 0:
            return dcc.Markdown(md_text)
        return None

    dash_dcc.start_server(app)

    dash_dcc.driver.execute_script(
        'window.hljs = {highlightElement: (block) => {block.innerHTML="hljs override"}};'
    )

    dash_dcc.find_element("#md-trigger").click()
    dash_dcc.wait_for_text_to_equal("#md-container code", "hljs override")

    assert dash_dcc.get_logs() == []
