import json
from multiprocessing import Value
import datetime
import itertools
import re
import dash_html_components as html
import dash_core_components as dcc
import dash_flow_example

import dash
import time

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

    def test_wildcard_callback(self):
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
                    html.Div(id='output-1', **{'data-cb': 'initial value',
                                               'aria-cb': 'initial value'})
                ])
            )
        ])

        input_call_count = Value('i', 0)

        @app.callback(Output('output-1', 'data-cb'), [Input('input', 'value')])
        def update_data(value):
            input_call_count.value = input_call_count.value + 1
            return value

        @app.callback(Output('output-1', 'children'),
                      [Input('output-1', 'data-cb')])
        def update_text(data):
            return data

        self.startServer(app)
        output1 = self.wait_for_element_by_id('output-1')
        wait_for(lambda: output1.text == 'initial value')
        self.percy_snapshot(name='wildcard-callback-1')

        input1 = self.wait_for_element_by_id('input')
        input1.clear()

        input1.send_keys('hello world')

        output1 = lambda: self.wait_for_element_by_id('output-1')
        wait_for(lambda: output1().text == 'hello world')
        self.percy_snapshot(name='wildcard-callback-2')

        self.assertEqual(
            input_call_count.value,
            # an initial call
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

    def test_wildcard_data_attributes(self):
        app = dash.Dash()
        test_time = datetime.datetime(2012, 1, 10, 2, 3)
        test_date = datetime.date(test_time.year, test_time.month,
                                  test_time.day)
        app.layout = html.Div([
            html.Div(
                id="inner-element",
                **{
                    'data-string': 'multiple words',
                    'data-number': 512,
                    'data-none': None,
                    'data-date': test_date,
                    'aria-progress': 5
                }
            )
        ], id='data-element')

        self.startServer(app)

        div = self.wait_for_element_by_id('data-element')

        # React wraps text and numbers with e.g. <!-- react-text: 20 -->
        # Remove those
        comment_regex = '<!--[^\[](.*?)-->'

        # Somehow the html attributes are unordered.
        # Try different combinations (they're all valid html)
        permutations = itertools.permutations([
            'id="inner-element"',
            'data-string="multiple words"',
            'data-number="512"',
            'data-date="%s"' % (test_date),
            'aria-progress="5"'
        ], 5)
        passed = False
        for i, permutation in enumerate(permutations):
            actual_cleaned = re.sub(comment_regex, '',
                                    div.get_attribute('innerHTML'))
            expected_cleaned = re.sub(
                comment_regex,
                '',
                "<div PERMUTE></div>"
                .replace('PERMUTE', ' '.join(list(permutation)))
            )
            passed = passed or (actual_cleaned == expected_cleaned)
            if passed:
                break
        if not passed:
            raise Exception(
                'HTML does not match\nActual:\n{}\n\nExpected:\n{}'.format(
                    actual_cleaned,
                    expected_cleaned
                )
            )

        assert_clean_console(self)

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

    def test_meta_tags(self):
        metas = (
            {'name': 'description', 'content': 'my dash app'},
            {'name': 'custom', 'content': 'customized'}
        )

        app = dash.Dash(meta_tags=metas)

        app.layout = html.Div(id='content')

        self.startServer(app)

        meta = self.driver.find_elements_by_tag_name('meta')

        # -1 for the meta charset.
        self.assertEqual(len(metas), len(meta) - 1, 'Not enough meta tags')

        for i in range(1, len(meta)):
            meta_tag = meta[i]
            meta_info = metas[i - 1]
            name = meta_tag.get_attribute('name')
            content = meta_tag.get_attribute('content')
            self.assertEqual(name, meta_info['name'])
            self.assertEqual(content, meta_info['content'])

    def test_index_customization(self):
        app = dash.Dash()

        app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
            </head>
            <body>
                <div id="custom-header">My custom header</div>
                <div id="add"></div>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                </footer>
                <div id="custom-footer">My custom footer</div>
                <script>
                // Test the formatting doesn't mess up script tags.
                var elem = document.getElementById('add');
                if (!elem) {
                    throw Error('could not find container to add');
                }
                elem.innerHTML = 'Got added';
                var config = {};
                fetch('/nonexist').then(r => r.json())
                    .then(r => config = r).catch(err => ({config}));
                </script>
            </body>
        </html>
        '''

        app.layout = html.Div('Dash app', id='app')

        self.startServer(app)

        time.sleep(0.5)

        header = self.wait_for_element_by_id('custom-header')
        footer = self.wait_for_element_by_id('custom-footer')

        self.assertEqual('My custom header', header.text)
        self.assertEqual('My custom footer', footer.text)

        add = self.wait_for_element_by_id('add')

        self.assertEqual('Got added', add.text)

        self.percy_snapshot('custom-index')

    def test_assets(self):
        app = dash.Dash(assets_folder='tests/assets')
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
                </footer>
            </body>
        </html>
        '''

        app.layout = html.Div([
            html.Div(id='content'),
            dcc.Input(id='test')
        ], id='layout')

        self.startServer(app)

        body = self.driver.find_element_by_tag_name('body')

        body_margin = body.value_of_css_property('margin')
        self.assertEqual('0px', body_margin)

        content = self.wait_for_element_by_id('content')
        content_padding = content.value_of_css_property('padding')
        self.assertEqual('8px', content_padding)

        tested = self.wait_for_element_by_id('tested')
        tested = json.loads(tested.text)
        self.assertEqual(3, len(tested))

        order = ('load_first', 'load_after', 'load_after1')

        for i in range(3):
            self.assertEqual(order[i], tested[i])

        self.percy_snapshot('test assets includes')

    def test_invalid_index_string(self):
        app = dash.Dash()

        def will_raise():
            app.index_string = '''
                    <!DOCTYPE html>
                    <html>
                        <head>
                            {%metas%}
                            <title>{%title%}</title>
                            {%favicon%}
                            {%css%}
                        </head>
                        <body>
                            <div id="custom-header">My custom header</div>
                            <div id="add"></div>
                            <footer>
                            </footer>
                        </body>
                    </html>
                    '''

        with self.assertRaises(Exception) as context:
            will_raise()

        app.layout = html.Div()
        self.startServer(app)

        exc_msg = str(context.exception)
        self.assertTrue('{%app_entry%}' in exc_msg)
        self.assertTrue('{%config%}' in exc_msg)
        self.assertTrue('{%scripts%}' in exc_msg)
        time.sleep(0.5)
        print('invalid index string')
