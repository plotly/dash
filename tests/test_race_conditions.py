import itertools
import time
import flask

from dash import Dash
from dash.dependencies import Input, Output, State, Event
import dash
import dash_html_components as html
import dash_core_components as dcc

from IntegrationTests import IntegrationTests
from utils import wait_for


class Tests(IntegrationTests):
    def setUp(self):
        pass

DELAY_TIME = 1

def create_race_conditions_test(endpoints):
    def test(self):
        app = Dash()
        app.layout = html.Div([
            html.Div('Hello world', id='output'),
            dcc.Input(id='input', value='initial value')
        ])
        app.scripts.config.serve_locally = True

        @app.callback(
            Output('output', 'content'),
            [Input('input', 'value')])
        def update(value):
            return value

        def delay():
            for i, route in enumerate(endpoints):
                if route in flask.request.path:
                    time.sleep((DELAY_TIME * i) + DELAY_TIME)

        def element_text(id):
            try:
                return self.driver.find_element_by_id(id).text
            except:
                return ''

        app.server.before_request(delay)
        self.startServer(app)

        total_delay = 0
        for i in routes:
            total_delay += DELAY_TIME*2 + DELAY_TIME
        time.sleep(total_delay + DELAY_TIME)

        wait_for(
            lambda: element_text('output') == 'initial value',
            lambda: '"{}" != "initial value"\nbody text: {}'.format(
                element_text('output'),
                element_text('react-entry-point')
            )
        )

        assert_clean_console(self)

    return test

routes = [
    'layout',
    'dependencies',
    '_config'
    # routes, component-suites, and update-component
    # are other endpoints but are excluded to speed up tests
]

for route_list in itertools.permutations(routes, len(routes)):
    setattr(
        Tests,
        'test_delayed_{}'.format(
            '_'.join([
                r.replace('-', ')') for r in route_list
            ])),
        create_race_conditions_test(route_list)
    )
