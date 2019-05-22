import json
import time
import itertools

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

        order = (
            'load_first', 'load_after', 'load_after1', 'load_after10',
            'load_after11', 'load_after2', 'load_after3', 'load_after4',
        )

        self.assertEqual(len(order), len(tested))

        for idx, _ in enumerate(tested):
            self.assertEqual(order[idx], tested[idx])

        self.percy_snapshot('test assets includes')

    def test_external_files_init(self):
        js_files = [
            'https://www.google-analytics.com/analytics.js',
            {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
            {
                'src': 'https://cdnjs.cloudflare.com/ajax/libs/ramda/0.26.1/ramda.min.js',
                'integrity': 'sha256-43x9r7YRdZpZqTjDT5E0Vfrxn1ajIZLyYWtfAXsargA=',
                'crossorigin': 'anonymous'
            },
            {
                'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.11/lodash.min.js',
                'integrity': 'sha256-7/yoZS3548fXSRXqc/xYzjsmuW3sFKzuvOCHd06Pmps=',
                'crossorigin': 'anonymous'
            }
        ]

        css_files = [
            'https://codepen.io/chriddyp/pen/bWLwgP.css',
            {
                'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
                'rel': 'stylesheet',
                'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
                'crossorigin': 'anonymous'
            }
        ]

        app = Dash(
            __name__, external_scripts=js_files, external_stylesheets=css_files)

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
                <div id="ramda-test"></div>
                <button type="button" id="btn">Btn</button>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''

        app.layout = html.Div()

        self.startServer(app)
        time.sleep(0.5)

        js_urls = [x['src'] if isinstance(x, dict) else x for x in js_files]
        css_urls = [x['href'] if isinstance(x, dict) else x for x in css_files]

        for fmt, url in itertools.chain(
                (("//script[@src='{}']", x) for x in js_urls),
                (("//link[@href='{}']", x) for x in css_urls)):
            self.driver.find_element_by_xpath(fmt.format(url))

        # Ensure the button style was overloaded by reset (set to 38px in codepen)
        btn = self.driver.find_element_by_id('btn')
        btn_height = btn.value_of_css_property('height')

        self.assertEqual('18px', btn_height)

        # ensure ramda was loaded before the assets so they can use it.
        lo_test = self.driver.find_element_by_id('ramda-test')
        self.assertEqual('Hello World', lo_test.text)
