import json

import dash_html_components as html
import dash_core_components as dcc

from dash import Dash
from tests.integration.IntegrationTests import IntegrationTests
from tests.integration.utils import wait_for, invincible

class TestAssets(IntegrationTests):

    def setUp(self):
        def wait_for_element_by_id(id_):
            wait_for(lambda: None is not invincible(
                lambda: self.driver.find_element_by_id(id_)
            ))
            return self.driver.find_element_by_id(id_)
        self.wait_for_element_by_id = wait_for_element_by_id

    def test_assets(self):
        app = Dash(__name__, assets_ignore='.*ignored.*')
        app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%css%}
            </head>
            <body>
                <div id="tested"></div>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''

        app.layout = html.Div([
            html.Div('Content', id='content'),
            dcc.Input(id='test')
        ], id='layout')

        self.startServer(app)

        # time.sleep(3600)

        body = self.driver.find_element_by_tag_name('body')

        body_margin = body.value_of_css_property('margin')
        self.assertEqual('0px', body_margin)

        content = self.wait_for_element_by_id('content')
        content_padding = content.value_of_css_property('padding')
        self.assertEqual('8px', content_padding)

        tested = self.wait_for_element_by_id('tested')
        tested = json.loads(tested.text)

        order = ('load_first', 'load_after', 'load_after1',
                 'load_after10', 'load_after11', 'load_after2',
                 'load_after3', 'load_after4', )

        self.assertEqual(len(order), len(tested))

        for idx, _ in enumerate(tested):
            self.assertEqual(order[idx], tested[idx])

        self.percy_snapshot('test assets includes')
