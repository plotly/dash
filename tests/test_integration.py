import json
from multiprocessing import Value
import datetime
import itertools
import re
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import dash_dangerously_set_inner_html
import dash_flow_example

import dash_html_components as html
import dash_core_components as dcc

import dash

from dash.dependencies import Input, Output, State
from dash.exceptions import (
    PreventUpdate, DuplicateCallbackOutput, CallbackException,
    MissingCallbackContextException, InvalidCallbackReturnValue
)
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

        self.wait_for_text_to_equal('#output-1', 'initial value')
        self.percy_snapshot(name='simple-callback-1')

        input1 = self.wait_for_element_by_id('input')

        chain = (ActionChains(self.driver)
                 .click(input1)
                 .send_keys(Keys.HOME)
                 .key_down(Keys.SHIFT)
                 .send_keys(Keys.END)
                 .key_up(Keys.SHIFT)
                 .send_keys(Keys.DELETE))
        chain.perform()

        input1.send_keys('hello world')

        self.wait_for_text_to_equal('#output-1', 'hello world')
        self.percy_snapshot(name='simple-callback-2')

        self.assertEqual(
            call_count.value,
            # an initial call to retrieve the first value
            # and one for clearing the input
            2 +
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
        self.wait_for_text_to_equal('#output-1', 'initial value')
        self.percy_snapshot(name='wildcard-callback-1')

        input1 = self.wait_for_element_by_css_selector('#input')
        chain = (ActionChains(self.driver)
                 .click(input1)
                 .send_keys(Keys.HOME)
                 .key_down(Keys.SHIFT)
                 .send_keys(Keys.END)
                 .key_up(Keys.SHIFT)
                 .send_keys(Keys.DELETE))
        chain.perform()

        input1.send_keys('hello world')

        self.wait_for_text_to_equal('#output-1', 'hello world')
        self.percy_snapshot(name='wildcard-callback-2')

        self.assertEqual(
            input_call_count.value,
            # an initial call
            # and a call for clearing the input
            2 +
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
        comment_regex = '<!--[^\[](.*?)-->'  # noqa: W605

        # Somehow the html attributes are unordered.
        # Try different combinations (they're all valid html)
        permutations = itertools.permutations([
            'id="inner-element"',
            'data-string="multiple words"',
            'data-number="512"',
            'data-date="%s"' % test_date,
            'aria-progress="5"'
        ], 5)
        passed = False
        for permutation in permutations:
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

    def test_no_props_component(self):
        app = dash.Dash()
        app.layout = html.Div([
            dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
                <h1>No Props Component</h1>
            ''')
        ])
        self.startServer(app)
        assert_clean_console(self)
        self.percy_snapshot(name='no-props-component')

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
        metas = [
            {'name': 'description', 'content': 'my dash app'},
            {'name': 'custom', 'content': 'customized'},
        ]

        app = dash.Dash(meta_tags=metas)

        app.layout = html.Div(id='content')

        self.startServer(app)

        meta = self.driver.find_elements_by_tag_name('meta')

        # -2 for the meta charset and http-equiv.
        self.assertEqual(len(metas), len(meta) - 2, 'Not enough meta tags')

        for i in range(2, len(meta)):
            meta_tag = meta[i]
            meta_info = metas[i - 2]
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
                    {%renderer%}
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
        app = dash.Dash(__name__,
                        assets_ignore='.*ignored.*')
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

        for i in range(len(tested)):
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

        app = dash.Dash(__name__,
                        external_scripts=js_files,
                        external_stylesheets=css_files)

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

    def test_func_layout_accepted(self):

        app = dash.Dash()

        def create_layout():
            return html.Div('Hello World')
        app.layout = create_layout

        self.startServer(app)
        time.sleep(0.5)

    def test_multi_output(self):
        app = dash.Dash(__name__)
        app.scripts.config.serve_locally = True

        app.layout = html.Div([
            html.Button('OUTPUT', id='output-btn'),

            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Output 1'),
                        html.Th('Output 2')
                    ])
                ]),
                html.Tbody([
                    html.Tr([html.Td(id='output1'), html.Td(id='output2')]),
                ])
            ]),

            html.Div(id='output3'),
            html.Div(id='output4'),
            html.Div(id='output5')
        ])

        @app.callback([Output('output1', 'children'), Output('output2', 'children')],
                      [Input('output-btn', 'n_clicks')],
                      [State('output-btn', 'n_clicks_timestamp')])
        def on_click(n_clicks, n_clicks_timestamp):
            if n_clicks is None:
                raise PreventUpdate

            return n_clicks, n_clicks_timestamp

        # Dummy callback for DuplicateCallbackOutput test.
        @app.callback(Output('output3', 'children'),
                      [Input('output-btn', 'n_clicks')])
        def dummy_callback(n_clicks):
            if n_clicks is None:
                raise PreventUpdate

            return 'Output 3: {}'.format(n_clicks)

        # Test that a multi output can't be included in a single output
        with self.assertRaises(DuplicateCallbackOutput) as context:
            @app.callback(Output('output1', 'children'),
                          [Input('output-btn', 'n_clicks')])
            def on_click_duplicate(n_clicks):
                if n_clicks is None:
                    raise PreventUpdate

                return 'something else'

        self.assertTrue('output1' in context.exception.args[0])

        # Test a multi output cannot contain a used single output
        with self.assertRaises(DuplicateCallbackOutput) as context:
            @app.callback([Output('output3', 'children'),
                           Output('output4', 'children')],
                          [Input('output-btn', 'n_clicks')])
            def on_click_duplicate_multi(n_clicks):
                if n_clicks is None:
                    raise PreventUpdate

                return 'something else'

        self.assertTrue('output3' in context.exception.args[0])

        with self.assertRaises(DuplicateCallbackOutput) as context:
            @app.callback([Output('output5', 'children'),
                           Output('output5', 'children')],
                          [Input('output-btn', 'n_clicks')])
            def on_click_same_output(n_clicks):
                return n_clicks

        self.assertTrue('output5' in context.exception.args[0])

        with self.assertRaises(DuplicateCallbackOutput) as context:
            @app.callback([Output('output1', 'children'),
                           Output('output5', 'children')],
                          [Input('output-btn', 'n_clicks')])
            def overlapping_multi_output(n_clicks):
                return n_clicks

        self.assertTrue(
            '{\'output1.children\'}' in context.exception.args[0]
            or "set(['output1.children'])" in context.exception.args[0]
        )

        self.startServer(app)

        t = time.time()

        btn = self.wait_for_element_by_id('output-btn')
        btn.click()
        time.sleep(1)

        self.wait_for_text_to_equal('#output1', '1')
        output2 = self.wait_for_element_by_css_selector('#output2')

        self.assertGreater(int(output2.text), t)

    def test_with_custom_renderer(self):
        app = dash.Dash(__name__)

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
                <div>Testing custom DashRenderer</div>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    <script id="_dash-renderer" type="application/javascript">
                        console.log('firing up a custom renderer!')
                        const renderer = new DashRenderer({
                            request_pre: () => {
                                var output = document.getElementById('output-pre')
                                if(output) {
                                    output.innerHTML = 'request_pre changed this text!';
                                }
                            },
                            request_post: () => {
                                var output = document.getElementById('output-post')
                                if(output) {
                                    output.innerHTML = 'request_post changed this text!';
                                }
                            }
                        })
                    </script>
                </footer>
                <div>With request hooks</div>
            </body>
        </html>
        '''

        app.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(
                html.Div([
                    html.Div(id='output-1'),
                    html.Div(id='output-pre'),
                    html.Div(id='output-post')
                ])
            )
        ])

        @app.callback(Output('output-1', 'children'), [Input('input', 'value')])
        def update_output(value):
            return value

        self.startServer(app)

        input1 = self.wait_for_element_by_id('input')
        chain = (ActionChains(self.driver)
                 .click(input1)
                 .send_keys(Keys.HOME)
                 .key_down(Keys.SHIFT)
                 .send_keys(Keys.END)
                 .key_up(Keys.SHIFT)
                 .send_keys(Keys.DELETE))
        chain.perform()

        input1.send_keys('fire request hooks')

        self.wait_for_text_to_equal('#output-1', 'fire request hooks')
        self.wait_for_text_to_equal('#output-pre', 'request_pre changed this text!')
        self.wait_for_text_to_equal('#output-post', 'request_post changed this text!')

        self.percy_snapshot(name='request-hooks')

    def test_with_custom_renderer_interpolated(self):

        renderer = '''
            <script id="_dash-renderer" type="application/javascript">
                console.log('firing up a custom renderer!')
                const renderer = new DashRenderer({
                    request_pre: () => {
                        var output = document.getElementById('output-pre')
                        if(output) {
                            output.innerHTML = 'request_pre changed this text!';
                        }
                    },
                    request_post: () => {
                        var output = document.getElementById('output-post')
                        if(output) {
                            output.innerHTML = 'request_post changed this text!';
                        }
                    }
                })
            </script>
        '''

        class CustomDash(dash.Dash):

            def interpolate_index(self, **kwargs):
                return '''
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>My App</title>
                    </head>
                    <body>

                        <div id="custom-header">My custom header</div>
                        {app_entry}
                        {config}
                        {scripts}
                        {renderer}
                        <div id="custom-footer">My custom footer</div>
                    </body>
                </html>
                '''.format(
                    app_entry=kwargs['app_entry'],
                    config=kwargs['config'],
                    scripts=kwargs['scripts'],
                    renderer=renderer)

        app = CustomDash()

        app.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(
                html.Div([
                    html.Div(id='output-1'),
                    html.Div(id='output-pre'),
                    html.Div(id='output-post')
                ])
            )
        ])

        @app.callback(Output('output-1', 'children'), [Input('input', 'value')])
        def update_output(value):
            return value

        self.startServer(app)

        input1 = self.wait_for_element_by_id('input')
        chain = (ActionChains(self.driver)
                 .click(input1)
                 .send_keys(Keys.HOME)
                 .key_down(Keys.SHIFT)
                 .send_keys(Keys.END)
                 .key_up(Keys.SHIFT)
                 .send_keys(Keys.DELETE))
        chain.perform()

        input1.send_keys('fire request hooks')

        self.wait_for_text_to_equal('#output-1', 'fire request hooks')
        self.wait_for_text_to_equal('#output-pre', 'request_pre changed this text!')
        self.wait_for_text_to_equal('#output-post', 'request_post changed this text!')

        self.percy_snapshot(name='request-hooks interpolated')

    def test_modified_response(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Input(id='input', value='ab'),
            html.Div(id='output')
        ])

        @app.callback(Output('output', 'children'), [Input('input', 'value')])
        def update_output(value):
            dash.callback_context.response.set_cookie(
                'dash cookie', value + ' - cookie')
            return value + ' - output'

        self.startServer(app)
        self.wait_for_text_to_equal('#output', 'ab - output')
        input1 = self.wait_for_element_by_id('input')

        input1.send_keys('cd')

        self.wait_for_text_to_equal('#output', 'abcd - output')
        cookie = self.driver.get_cookie('dash cookie')
        # cookie gets json encoded
        self.assertEqual(cookie['value'], '"abcd - cookie"')

        assert_clean_console(self)

    def test_late_component_register(self):
        app = dash.Dash()

        app.layout = html.Div([
            html.Button('Click me to put a dcc ', id='btn-insert'),
            html.Div(id='output')
        ])

        @app.callback(Output('output', 'children'),
                      [Input('btn-insert', 'n_clicks')])
        def update_output(value):
            if value is None:
                raise PreventUpdate

            return dcc.Input(id='inserted-input')

        self.startServer(app)

        btn = self.wait_for_element_by_css_selector('#btn-insert')
        btn.click()
        time.sleep(1)

        self.wait_for_element_by_css_selector('#inserted-input')

    def test_output_input_invalid_callback(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.Div('child', id='input-output'),
            html.Div(id='out')
        ])

        with self.assertRaises(CallbackException) as context:
            @app.callback(Output('input-output', 'children'),
                          [Input('input-output', 'children')])
            def failure(children):
                pass

        self.assertEqual(
            'Same output and input: input-output.children',
            context.exception.args[0]
        )

        # Multi output version.
        with self.assertRaises(CallbackException) as context:
            @app.callback([Output('out', 'children'),
                           Output('input-output', 'children')],
                          [Input('input-output', 'children')])
            def failure2(children):
                pass

        self.assertEqual(
            'Same output and input: input-output.children',
            context.exception.args[0]
        )

    def test_callback_return_validation(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.Div(id='a'),
            html.Div(id='b'),
            html.Div(id='c'),
            html.Div(id='d'),
            html.Div(id='e'),
            html.Div(id='f')
        ])

        @app.callback(Output('b', 'children'), [Input('a', 'children')])
        def single(a):
            # anything non-serializable, really
            return set([1])

        with self.assertRaises(InvalidCallbackReturnValue):
            single('aaa')

        @app.callback([Output('c', 'children'), Output('d', 'children')],
                      [Input('a', 'children')])
        def multi(a):
            # non-serializable inside a list
            return [1, set([2])]

        with self.assertRaises(InvalidCallbackReturnValue):
            multi('aaa')

        @app.callback([Output('e', 'children'), Output('f', 'children')],
                      [Input('a', 'children')])
        def multi2(a):
            # wrong-length list
            return ['abc']

        with self.assertRaises(InvalidCallbackReturnValue):
            multi2('aaa')

    def test_callback_context(self):
        app = dash.Dash(__name__)

        btns = ['btn-{}'.format(x) for x in range(1, 6)]

        app.layout = html.Div([
            html.Div([
                html.Button(x, id=x) for x in btns
            ]),
            html.Div(id='output'),
        ])

        @app.callback(Output('output', 'children'),
                      [Input(x, 'n_clicks') for x in btns])
        def on_click(*args):
            if not dash.callback_context.triggered:
                raise PreventUpdate
            trigger = dash.callback_context.triggered[0]
            return 'Just clicked {} for the {} time!'.format(
                trigger['prop_id'].split('.')[0], trigger['value']
            )

        self.startServer(app)

        btn_elements = [
            self.wait_for_element_by_id(x) for x in btns
        ]

        for i in range(1, 5):
            for j, btn in enumerate(btns):
                btn_elements[j].click()
                self.wait_for_text_to_equal(
                    '#output',
                    'Just clicked {} for the {} time!'.format(
                        btn, i
                    )
                )

    def test_no_callback_context(self):
        for attr in ['inputs', 'states', 'triggered', 'response']:
            with self.assertRaises(MissingCallbackContextException):
                getattr(dash.callback_context, attr)
