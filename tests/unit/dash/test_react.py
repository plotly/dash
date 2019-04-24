import unittest
import json
import pkgutil
import plotly
from dash_html_components import Div
import dash_renderer
import dash_core_components as dcc
import dash

from dash.dependencies import Input, Output, State
from dash import exceptions


def generate_css(css_links):
    return '\n'.join([
        '<link rel="stylesheet" href="{}">'.format(l)
        for l in css_links
    ])


def generate_js(js_links):
    return '\n'.join([
        '<script src="{}"></script>'.format(l)
        for l in js_links
    ])


class TestCallbacks(unittest.TestCase):
    def test_callback_registry(self):
        app = dash.Dash('')
        input = dcc.Input(id='input')

        app.layout = Div([
            input,
            Div(id='output-1'),
            Div(id='output-2'),
            Div(id='output-3')
        ], id='body')

        app.callback(
            Output('body', 'children'),
            [Input('input', 'value')]
        )
        app.callback(
            Output('output-1', 'children'),
            [Input('input', 'value')]
        )
        app.callback(
            Output('output-2', 'children'),
            [Input('input', 'value')],
            state=[State('input', 'value')],
        )
        app.callback(
            Output('output-3', 'children'),
            [Input('input', 'value')],
            state=[State('input', 'value')]
        )

    def test_no_layout_exception(self):
        app = dash.Dash('')
        self.assertRaises(
            exceptions.LayoutIsNotDefined,
            app.callback,
            Output('body', 'children'),
            [Input('input', 'value')]
        )

    def test_exception_id_not_in_layout(self):
        app = dash.Dash('')
        app.layout = Div('', id='test')
        self.assertRaises(
            exceptions.NonExistentIdException,
            app.callback,
            Output('output', 'children'),
            [Input('input', 'value')]
        )

    def test_exception_prop_not_in_component(self):
        app = dash.Dash('')
        app.layout = Div([
            dcc.Input(id='input'),
            Div(id='output')
        ], id='body')

        self.assertRaises(
            exceptions.NonExistentPropException,
            app.callback,
            Output('output', 'non-there'),
            [Input('input', 'value')]
        )

        self.assertRaises(
            exceptions.NonExistentPropException,
            app.callback,
            Output('output', 'children'),
            [Input('input', 'valuez')]
        )

        self.assertRaises(
            exceptions.NonExistentPropException,
            app.callback,
            Output('body', 'childrenz'),
            [Input('input', 'value')]
        )

    def test_exception_event_not_in_component(self):
        # no events anymore, period!
        app = dash.Dash('')
        app.layout = Div([
            Div(id='button'),
            Div(id='output'),
            Div(id='graph-output'),
            dcc.Graph(id='graph')
        ], id='body')

        for id in ['output', 'body']:
            self.assertRaises(
                TypeError,
                app.callback,
                Output(id, 'children'),
                events=[]
            )

    @unittest.skip('leave for future refactoring')
    def test_exception_component_is_not_right_type(self):
        app = dash.Dash('')
        app.layout = Div([
            dcc.Input(id='input'),
            Div(id='output')
        ], id='body')

        test_args = [
            [Output('output', 'children'), Input('input', 'value'), []],
            [Output('output', 'children'), [], State('input', 'value')],
        ]
        for args in test_args:
            self.assertRaises(
                exceptions.IncorrectTypeException,
                app.callback,
                *args
            )

    def test_suppress_callback_exception(self):
        app = dash.Dash('')
        app.layout = Div([
            dcc.Input(id='input'),
            Div(id='output')
        ], id='body')
        self.assertRaises(
            exceptions.NonExistentIdException,
            app.callback,
            Output('id-not-there', 'children'),
            [Input('input', 'value')]
        )
        app.config.supress_callback_exceptions = True
        app.callback(Output('id-not-there', 'children'),
                     [Input('input', 'value')])

    def test_missing_inputs(self):
        app = dash.Dash('')
        app.layout = Div([
            dcc.Input(id='input')
        ], id='body')
        self.assertRaises(
            exceptions.MissingInputsException,
            app.callback,
            Output('body', 'children'),
            [],
            [State('input', 'value')]
        )
