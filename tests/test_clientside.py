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
        app = Dash(__name__, assets_folder='test_clientside')

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
