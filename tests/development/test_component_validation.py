import os
import json
import unittest
import collections
from dash.development.component_loader import _get_metadata
from dash.development.base_component import generate_class, Component
from dash.development.validator import DashValidator


class TestGenerateClass(unittest.TestCase):
    def setUp(self):
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
        self.assertTrue(self.component_validator.validate({
            'optionalString': None
        }))

    def test_boolean_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalBool': False
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalBool': "False"
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalBool': None
        }))

    def test_number_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalNumber': 7
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalNumber': "seven"
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalNumber': None
        }))

    def test_object_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalObject': {'foo': 'bar'}
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalObject': "not a dict"
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalObject': None
        }))

    def test_node_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalNode': 7
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalNode': "seven"
        }))
        self.assertTrue(self.component_validator.validate({
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
        self.assertTrue(self.component_validator.validate({
            'optionalElement': None
        }))

    def test_enum_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalEnum': "News"
        }))
        self.assertTrue(self.component_validator.validate({
            'optionalEnum': "Photos"
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalEnum': "not_in_enum"
        }))
        self.assertTrue(self.component_validator.validate({
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
        self.assertTrue(self.component_validator.validate({
            'optionalUnion': None
        }))

    def test_arrayof_validation(self):
        self.assertTrue(self.component_validator.validate({
            'optionalArrayOf': [1, 2, 3]
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalArrayOf': 7
        }))
        self.assertFalse(self.component_validator.validate({
            'optionalArrayOf': ["one", "two", "three"]
        }))
        self.assertTrue(self.component_validator.validate({
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
        self.assertTrue(self.component_validator.validate({
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
        self.assertTrue(self.component_validator.validate({
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
        self.assertTrue(self.component_validator.validate({
            'optionalAny': None
        }))
