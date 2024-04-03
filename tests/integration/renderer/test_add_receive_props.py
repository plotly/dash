from dash import Dash, html

from dash_test_components import AddPropsComponent, ReceivePropsComponent


def test_dvui001_add_receive_props(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            AddPropsComponent(
                ReceivePropsComponent(
                    id='test-receive1',
                    text='receive component1',
                ),
                id='test-add'
            ),
            ReceivePropsComponent(
                id='test-receive2',
                text='receive component2',
            ),
        ]
    )

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
        dev_tools_props_check=False,
    )
