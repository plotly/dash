from .IntegrationTests import IntegrationTests
import dash
import dash_html_components as html
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

from dash_table import Table  # pylint: disable=no-name-in-module

class Tests(IntegrationTests):
    # Tests are dynamically generated below
    pass


def create_test(test_case):
    def test(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.Div(id='waitfor'),
            Table(**test_case['props'])
        ])

        self.startServer(app)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "waitfor"))
        )

        self.percy_snapshot(test_case['name'])

    return test


with open(os.path.join('tests', 'fixtures.json'), 'r') as f:
    SAMPLE_TABLE_PROPS = json.loads(f.read())

for test_data in SAMPLE_TABLE_PROPS:
    test_func = create_test(test_data)
    setattr(
        Tests,
        'test_{}'.format(test_data['name']),
        test_func
    )
