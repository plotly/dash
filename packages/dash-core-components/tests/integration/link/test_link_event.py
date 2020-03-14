import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html


def test_link001_event(dash_dcc):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Link("Page 1", id="link1", href="/page-1"),
            dcc.Location(id="url", refresh=False),
            html.Div(id='content'),
        ]
    )

    @app.callback(Output("content", "children"), [Input("url", "pathname")])
    def display_page(pathname):
        if pathname is None or pathname == "/page-1":
            return html.Div("1", id="div1")
        elif pathname == "/":
            return html.Div("base", id="div0")
        else:
            return "404"

    dash_dcc.start_server(app)
    dash_dcc.driver.execute_script(
        '''
        window.addEventListener('_dashprivate_pushstate', function() {
            window._test_link_event_counter = (window._test_link_event_counter || 0) + 1;
        });

        window.addEventListener('_dashprivate_historychange', function() {
            window._test_history_event_counter = (window._test_history_event_counter || 0) + 1;
        });
    '''
    )

    dash_dcc.wait_for_element_by_id("div0")

    dash_dcc.find_element('#link1').click()

    dash_dcc.wait_for_element_by_id("div1")

    link_counter = dash_dcc.driver.execute_script(
        '''
        return window._test_link_event_counter;
    '''
    )

    history_counter = dash_dcc.driver.execute_script(
        '''
        return window._test_history_event_counter;
    '''
    )

    assert link_counter == 1
    assert history_counter == 1
