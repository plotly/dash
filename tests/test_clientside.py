import dash
from dash.dependencies import Input, Output, State, ClientFunction
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .IntegrationTests import IntegrationTests
from multiprocessing import Value


class Tests(IntegrationTests):
    def setUp(self):
        pass

    def test_simple_clientside_serverside_callback(self):
        app = dash.Dash(__name__, assets_folder='test_clientside')

        app.layout = html.Div([
            dcc.Input(id='input'),
            html.Div(id='output-clientside'),
            html.Div(id='output-serverside')
        ])


        @app.callback(
            Output('output-serverside', 'children'),
            [Input('input', 'value')])
        def update_output(value):
            return 'Server says "{}"'.format(value)


        app.callback(
            Output('output-clientside', 'children'),
            [Input('input', 'value')],
            client_function=ClientFunction(
                namespace='clientside',
                function_name='display'
            )
        )

        self.startServer(app)

        input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "input"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, 'output-serverside'),
                'Server says "None"'
            )
        )

        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, 'output-clientside'),
                'Client says "undefined"'
            )
        )

        input.send_keys('hello world')
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, 'output-serverside'),
                'Server says "hello world"'
            )
        )
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, 'output-clientside'),
                'Client says "hello world"'
            )
        )


    def test_chained_serverside_clientside_callbacks(self):
        app = dash.Dash(__name__, assets_folder='test_clientside')

        app.layout = html.Div([

            html.Label('x'),
            dcc.Input(id='x', value=3),

            html.Label('y'),
            dcc.Input(id='y', value=6),

            # clientside
            html.Label('x + y (clientside)'),
            dcc.Input(id='x+y'),

            # server-side
            html.Label('x+y / 2 (serverside)'),
            dcc.Input(id='x+y / 2'),

            # server-side
            html.Div([
                html.Label('Display x, y, x+y/2 (serverside)'),
                dcc.Textarea(id='display-all-of-the-values'),
            ]),

            # clientside
            html.Label('Mean(x, y, x+y, x+y/2) (clientside)'),
            dcc.Input(id='mean-of-all-values'),

        ])

        app.callback(
            Output('x+y', 'value'),
            [Input('x', 'value'),
             Input('y', 'value')],
            client_function=ClientFunction('R', 'add'))

        call_counts = {
            'divide': Value('i', 0),
            'display': Value('i', 0)
        }

        @app.callback(Output('x+y / 2', 'value'),
                      [Input('x+y', 'value')])
        def divide_by_two(value):
            call_counts['divide'].value += 1
            return float(value) / 2.0

        @app.callback(Output('display-all-of-the-values', 'value'),
                      [Input('x', 'value'),
                       Input('y', 'value'),
                       Input('x+y', 'value'),
                       Input('x+y / 2', 'value')])
        def display_all(*args):
            call_counts['display'].value += 1
            return '\n'.join([str(a) for a in args])

        app.callback(
            Output('mean-of-all-values', 'value'),
            [Input('x', 'value'), Input('y', 'value'),
             Input('x+y', 'value'), Input('x+y / 2', 'value')],
            client_function=ClientFunction('clientside', 'mean'))

        self.startServer(app)

        def run_assertions(assertions):
            for id in assertions:
                WebDriverWait(self.driver, 10).until(
                    EC.text_to_be_present_in_element_value(
                        (By.ID, id),
                        assertions[id]
                    ),
                    message='Failed assertion: #{}.value != {}'.format(
                        id, assertions[id]
                    )
                )

        run_assertions({
            'x': '3',
            'y': '6',
            'x+y': '9',
            'x+y / 2': '4.5',
            'display-all-of-the-values': '3\n6\n9\n4.5',
            'mean-of-all-values': str((3+6+9+4.5) / 4.0)
        })
        self.assertEqual(call_counts['display'].value, 1)
        self.assertEqual(call_counts['divide'].value, 1)

        x_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'x'))
        )
        x_input.send_keys('1')

        run_assertions({
            'x': '31',
            'y': '6',
            'x+y': '37',
            'x+y / 2': '18.5',
            'display-all-of-the-values': '31\n6\n37\n18.5',
            'mean-of-all-values': str((31+6+37+18.5) / 4.0)
        })
        self.assertEqual(call_counts['display'].value, 2)
        self.assertEqual(call_counts['divide'].value, 2)
