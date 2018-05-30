from .IntegrationTests import IntegrationTests
import dash
import dash_html_components as html
import dash_core_components as dcc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dash_table import Table


class EventTests(IntegrationTests):

    def test_selection_active_focus(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Input(value='', placeholder='type here', type='text',
                      id='textinput'),
            Table(
                columns=[
                    {'id': 'aaa', 'name': 'cheese'},
                    {'id': 'bbb', 'name': 'tomato'},
                ],
                dataframe=[
                    {'aaa': 1, 'bbb': 3},
                    {'aaa': 2, 'bbb': 2},
                    {'aaa': 3, 'bbb': 1}
                ]
            )
        ])
        self.startServer(app)

        try:
            import ipdb
            ipdb.set_trace()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "waitfor"))
            )
        finally:
            self.driver.quit()
