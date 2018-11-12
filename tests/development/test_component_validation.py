import os
import json
import unittest
import collections
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_html_components as html
from importlib import import_module
from dash.development.component_loader import _get_metadata
from dash.development.base_component import generate_class, Component
from dash.development.validator import DashValidator

# Monkey patched html
html.Div._schema = {'children': {'anyof': [{'type': 'string'}, {'type': 'number'}, {'type': 'boolean'}, {'type': 'component'}, {'allowed': [None], 'type': ('string', 'number'), 'nullable': True}, {'type': 'list', 'schema': {'anyof': [{'type': 'string'}, {'type': 'number'}, {'type': 'boolean'}, {'type': 'component'}, {'allowed': [None], 'type': ('string', 'number'), 'nullable': True}], 'nullable': True}}], 'nullable': True}}
html.Button._schema = html.Div._schema

class TestComponentValidation(unittest.TestCase):
    def setUp(self):
        self.validator = DashValidator
        path = os.path.join('tests', 'development', 'metadata_test.json')
        data = _get_metadata(path)

        self.ComponentClass = generate_class(
            typename='Table',
            props=data['props'],
            description=data['description'],
            namespace='TableComponents'
        )

        path = os.path.join(
            'tests', 'development', 'metadata_required_test.json'
        )
        with open(path) as data_file:
            json_string = data_file.read()
            required_data = json\
                .JSONDecoder(object_pairs_hook=collections.OrderedDict)\
                .decode(json_string)
            self.required_data = required_data

        self.ComponentClassRequired = generate_class(
            typename='TableRequired',
            props=required_data['props'],
            description=required_data['description'],
            namespace='TableComponents'
        )

        DashValidator.set_component_class(Component)

        def make_validator(schema):
            return DashValidator(schema, allow_unknown=True)

        self.component_validator = make_validator(self.ComponentClass._schema)
        self.required_validator =\
            make_validator(self.ComponentClassRequired._schema)
        self.figure_validator = make_validator({
            'figure': {
                'validator': 'plotly_figure'
            }
        })
        self.options_validator = make_validator({
            'options': {
                'validator': 'options_with_unique_values'
            }
        })

    def test_component_in_initial_layout_is_validated(self):
        app = dash.Dash(__name__)
        app.config['suppress_callback_exceptions'] = True

        app.layout = html.Div(self.ComponentClass(id='hello', children=[[]]))

        with self.assertRaises(
            dash.exceptions.ComponentInitializationValidationError
        ) as cm:
            app._validate_layout()
        the_exception = cm.exception
        print(the_exception)

    def test_callback_output_is_validated(self):
        app = dash.Dash(__name__)
        app.config['suppress_callback_exceptions'] = True

        app.layout = html.Div(children=[
            html.Button(id='put-components', children='Click me'),
            html.Div(id='container'),
        ])

        @app.callback(
            dash.dependencies.Output('container', 'children'),
            [dash.dependencies.Input('put-components', 'n_clicks')]
        )
        def put_components(n_clicks):
            if n_clicks:
                return [[]]
            return "empty"

        with app.server.test_request_context(
            "/_dash-update-component",
            json={
                'inputs': [{
                    'id': 'put-components',
                    'property': 'n_clicks',
                    'value': 1
                }],
                'output': {
                    'namespace': 'dash_html_components',
                    'type': 'Div',
                    'id': 'container',
                    'property': 'children'
                }
            }
        ):
            with self.assertRaises(
                dash.exceptions.CallbackOutputValidationError
            ) as cm:
                app.dispatch()
            the_exception = cm.exception
            print(the_exception)

    def test_component_initialization_in_callback_is_validated(self):
        app = dash.Dash(__name__)
        app.config['suppress_callback_exceptions'] = True

        app.layout = html.Div(children=[
            html.Button(id='put-components', children='Click me'),
            html.Div(id='container'),
        ])

        @app.callback(
            dash.dependencies.Output('container', 'children'),
            [dash.dependencies.Input('put-components', 'n_clicks')]
        )
        def put_components(n_clicks):
            if n_clicks:
                return html.Button(
                    children=[[]],
                )
            return "empty"

        with app.server.test_request_context(
            "/_dash-update-component",
            json={
                'inputs': [{
                    'id': 'put-components',
                    'property': 'n_clicks',
                    'value': 1
                }],
                'output': {
                    'namespace': 'dash_html_components',
                    'type': 'Div',
                    'id': 'container',
                    'property': 'children'
                }
            }
        ):
            self.assertRaises(
                dash.exceptions.ComponentInitializationValidationError,
                app.dispatch
            )

    def test_required_validation(self):
        self.assertTrue(self.required_validator.validate({
            'id': 'required',
            'children': 'hello world'
        }))
        self.assertFalse(self.required_validator.validate({
            'children': 'hello world'
        }))

    def test_string_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalString': "bananas"
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalString': 7
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalString': None
        }))

    def test_boolean_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalBool': False
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalBool': "False"
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalBool': None
        }))

    def test_number_validation(self):
        numpy_types = [
            np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
            np.uint8, np.uint16, np.uint32, np.uint64,
            np.float_, np.float32, np.float64
        ]
        for t in numpy_types:
            self.assertTrue(self.component_validator.validate({
                'optionalNumber': t(7)
            }))
        self.assertTrue(self.component_validator.validate({
            'optionalNumber': 7
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalNumber': "seven"
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalNumber': None
        }))

    def test_object_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalObject': {'foo': 'bar'}
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObject': "not a dict"
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObject': self.ComponentClass()
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObject': None
        }))

    def test_children_validation(self):
        self.assertTrue(self.component_validator.validate({}))
        self.assertTrue(self.component_validator.validate({
            'children': None
        }))
        self.assertTrue(self.component_validator.validate({
            'children': 'one'
        }))
        self.assertTrue(self.component_validator.validate({
            'children': 1
        }))
        self.assertTrue(self.component_validator.validate({
            'children': False
        }))
        self.assertTrue(self.component_validator.validate({
            'children': self.ComponentClass()
        }))
        self.assertTrue(self.component_validator.validate({
            'children': ['one']
        }))
        self.assertTrue(self.component_validator.validate({
            'children': [1]
        }))
        self.assertTrue(self.component_validator.validate({
            'children': [self.ComponentClass()]
        }))
        self.assertTrue(self.component_validator.validate({
            'children': [None]
        }))
        self.assertTrue(self.component_validator.validate({
            'children': ()
        }))
        self.assertFalse(self.component_validator.validate({
            'children': [[]]
        }))

    def test_node_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalNode': 7
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalNode': "seven"
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalNode': None
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalNode': False
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalNode': self.ComponentClass()
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalNode': [
                7,
                'seven',
                False,
                self.ComponentClass()
            ]
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalNode': [["Invalid Nested Dict"]]
        }))

    def test_element_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalElement': self.ComponentClass()
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalElement': 7
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalElement': "seven"
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalElement': False
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalElement': None
        }))

    def test_enum_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalEnum': "News"
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalEnum': "Photos"
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalEnum': 1
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalEnum': 1.0
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalEnum': "1"
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalEnum': True
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalEnum': False
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalEnum': "not_in_enum"
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalEnum': None
        }))

    def test_union_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalUnion': "string"
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalUnion': 7
        }))
        # These will pass since propTypes.instanceOf(Message)
        # is used in the union. We cannot validate this value, so
        # we must accept everything since anything could be valid.
        # TODO: Find some sort of workaround

        # self.assertFalse(self.component_validator.validate({
        #     'optionalUnion': self.ComponentClass()
        # }))
        # self.assertFalse(self.component_validator.validate({
        #     'optionalUnion': [1, 2, 3]
        # }))
        self.assertFalse(self.component_validator.validate({
            'optionalUnion': None
        }))

    def test_arrayof_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalArrayOf': [1, 2, 3]
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalArrayOf': np.array([1, 2, 3])
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalArrayOf': pd.Series([1, 2, 3])
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalArrayOf': 7
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalArrayOf': ["one", "two", "three"]
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalArrayOf': None
        }))

    def test_objectof_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalObjectOf': {'one': 1, 'two': 2, 'three': 3}
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObjectOf': {'one': 1, 'two': '2', 'three': 3}
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObjectOf': [1, 2, 3]
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObjectOf': None
        }))

    def test_object_with_shape_and_nested_description_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalObjectWithShapeAndNestedDescription': {
                'color': "#431234",
                'fontSize': 2,
                'figure': {
                    'data': [{'object_1': "hey"}, {'object_2': "ho"}],
                    'layout': {"my": "layout"}
                },
            }
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObjectWithShapeAndNestedDescription': {
                'color': False,
                'fontSize': 2,
                'figure': {
                    'data': [{'object_1': "hey"}, {'object_2': "ho"}],
                    'layout': {"my": "layout"}
                },
            }
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObjectWithShapeAndNestedDescription': {
                'color': "#431234",
                'fontSize': "BAD!",
                'figure': {
                    'data': [{'object_1': "hey"}, {'object_2': "ho"}],
                    'layout': {"my": "layout"}
                },
            }
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObjectWithShapeAndNestedDescription': {
                'color': "#431234",
                'fontSize': 2,
                'figure': {
                    'data': [{'object_1': "hey"}, 7],
                    'layout': {"my": "layout"}
                },
            }
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObjectWithShapeAndNestedDescription': {
                'color': "#431234",
                'fontSize': 2,
                'figure': {
                    'data': [{'object_1': "hey"}, {'object_2': "ho"}],
                    'layout': ["my", "layout"]
                },
            }
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObjectWithShapeAndNestedDescription': None
        }))

    def test_any_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalAny': 7
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalAny': "seven"
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalAny': False
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalAny': []
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalAny': {}
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalAny': self.ComponentClass()
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalAny': None
        }))

    def test_figure_validation(self):
        self.assertFalse(self.figure_validator.validate({
            'figure': 7
        }))
        self.assertFalse(self.figure_validator.validate({
            'figure': {}
        }))
        self.assertTrue(self.figure_validator.validate({
            'figure': {'data': [{'x': [1, 2, 3],
                                 'y': [1, 2, 3],
                                 'type': 'scatter'}]}
        }))
        self.assertTrue(self.figure_validator.validate({
            'figure': go.Figure(
                data=[go.Scatter(x=[1, 2, 3], y=[1, 2, 3])],
                layout=go.Layout()
            )
        }))
        self.assertFalse(self.figure_validator.validate({
            'figure': {'doto': [{'x': [1, 2, 3],
                                 'y': [1, 2, 3],
                                 'type': 'scatter'}]}
        }))
        self.assertFalse(self.figure_validator.validate({
            'figure': None
        }))

    def test_options_validation(self):
        self.assertFalse(self.options_validator.validate({
            'options': [
                {'value': 'value1', 'label': 'label1'},
                {'value': 'value1', 'label': 'label1'}
            ]
        }))
        self.assertTrue(self.options_validator.validate({
            'options': [
                {'value': 'value1', 'label': 'label1'},
                {'value': 'value2', 'label': 'label2'}
            ]
        }))
