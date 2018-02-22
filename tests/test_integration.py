from multiprocessing import Value
import dash_html_components as html
import dash_core_components as dcc
import dash_flow_example
import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from .IntegrationTests import IntegrationTests
from .utils import assert_clean_console, invincible, wait_for


class Tests(IntegrationTests):
    def setUp(self):
        def wait_for_element_by_id(id):
            wait_for(lambda: None is not invincible(
                lambda: self.driver.find_element_by_id(id)
            ))
            return self.driver.find_element_by_id(id)
        self.wait_for_element_by_id = wait_for_element_by_id

    def test_simple_callback(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(
                html.Div([
                    1.5,
                    None,
                    'string',
                    html.Div(id='output-1')
                ])
            )
        ])

        call_count = Value('i', 0)

        @app.callback(Output('output-1', 'children'), [Input('input', 'value')])
        def update_output(value):
            call_count.value = call_count.value + 1
            return value

        self.startServer(app)

        output1 = self.wait_for_element_by_id('output-1')
        wait_for(lambda: output1.text == 'initial value')
        self.percy_snapshot(name='simple-callback-1')

        input1 = self.wait_for_element_by_id('input')
        input1.clear()

        input1.send_keys('hello world')

        output1 = lambda: self.wait_for_element_by_id('output-1')
        wait_for(lambda: output1().text == 'hello world')
        self.percy_snapshot(name='simple-callback-2')

        self.assertEqual(
            call_count.value,
            # an initial call to retrieve the first value
            1 +
            # one for each hello world character
            len('hello world')
        )

        assert_clean_console(self)

    def test_aborted_callback(self):
        """Raising PreventUpdate prevents update and triggering dependencies"""

        initial_input = 'initial input'
        initial_output = 'initial output'

        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Input(id='input', value=initial_input),
            html.Div(initial_output, id='output1'),
            html.Div(initial_output, id='output2'),
        ])

        callback1_count = Value('i', 0)
        callback2_count = Value('i', 0)

        @app.callback(Output('output1', 'children'), [Input('input', 'value')])
        def callback1(value):
            callback1_count.value = callback1_count.value + 1
            raise PreventUpdate("testing callback does not update")
            return value

        @app.callback(Output('output2', 'children'), [Input('output1', 'children')])
        def callback2(value):
            callback2_count.value = callback2_count.value + 1
            return value

        self.startServer(app)

        input_ = self.wait_for_element_by_id('input')
        input_.clear()
        input_.send_keys('x')
        output1 = self.wait_for_element_by_id('output1')
        output2 = self.wait_for_element_by_id('output2')

        # callback1 runs twice (initial page load and through send_keys)
        self.assertEqual(callback1_count.value, 2)

        # callback2 is never triggered, even on initial load
        self.assertEqual(callback2_count.value, 0)

        # double check that output1 and output2 children were not updated
        self.assertEqual(output1.text, initial_output)
        self.assertEqual(output2.text, initial_output)

        assert_clean_console(self)

        self.percy_snapshot(name='aborted')

    def test_flow_component(self):
        app = dash.Dash()

        app.layout = html.Div([
            dash_flow_example.ExampleReactComponent(
                id='react',
                value='my-value',
                label='react component'
            ),
            dash_flow_example.ExampleFlowComponent(
                id='flow',
                value='my-value',
                label='flow component'
            ),
            html.Hr(),
            html.Div(id='output')
        ])

        @app.callback(Output('output', 'children'),
                      [Input('react', 'value'), Input('flow', 'value')])
        def display_output(react_value, flow_value):
            return html.Div([
                'You have entered {} and {}'.format(react_value, flow_value),
                html.Hr(),
                html.Label('Flow Component Docstring'),
                html.Pre(dash_flow_example.ExampleFlowComponent.__doc__),
                html.Hr(),
                html.Label('React PropTypes Component Docstring'),
                html.Pre(dash_flow_example.ExampleReactComponent.__doc__),
                html.Div(id='waitfor')
            ])

        self.startServer(app)
        self.wait_for_element_by_id('waitfor')
        self.percy_snapshot(name='flowtype')
