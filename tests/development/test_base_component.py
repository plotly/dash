from collections import OrderedDict
import collections
import inspect
import json
import os
import shutil
import unittest
import plotly

from dash.development.base_component import (
    generate_class,
    generate_class_string,
    generate_class_file,
    Component,
    _explicitize_args,
    js_to_py_type,
    create_docstring,
    parse_events
)

Component._prop_names = ('id', 'a', 'children', 'style', )
Component._type = 'TestComponent'
Component._namespace = 'test_namespace'
Component._valid_wildcard_attributes = ['data-', 'aria-']


def nested_tree():
    """This tree has a few unique properties:
    - children is mixed strings and components (as in c2)
    - children is just components (as in c)
    - children is just strings (as in c1)
    - children is just a single component (as in c3, c4)
    - children contains numbers (as in c2)
    - children contains "None" items (as in c2)
    """
    c1 = Component(
        id='0.1.x.x.0',
        children='string'
    )
    c2 = Component(
        id='0.1.x.x',
        children=[10, None, 'wrap string', c1, 'another string', 4.51]
    )
    c3 = Component(
        id='0.1.x',
        # children is just a component
        children=c2
    )
    c4 = Component(
        id='0.1',
        children=c3
    )
    c5 = Component(id='0.0')
    c = Component(id='0', children=[c5, c4])
    return c, c1, c2, c3, c4, c5


class TestComponent(unittest.TestCase):
    def test_init(self):
        Component(a=3)

    def test_get_item_with_children(self):
        c1 = Component(id='1')
        c2 = Component(children=[c1])
        self.assertEqual(c2['1'], c1)

    def test_get_item_with_children_as_component_instead_of_list(self):
        c1 = Component(id='1')
        c2 = Component(id='2', children=c1)
        self.assertEqual(c2['1'], c1)

    def test_get_item_with_nested_children_one_branch(self):
        c1 = Component(id='1')
        c2 = Component(id='2', children=[c1])
        c3 = Component(children=[c2])
        self.assertEqual(c2['1'], c1)
        self.assertEqual(c3['2'], c2)
        self.assertEqual(c3['1'], c1)

    def test_get_item_with_nested_children_two_branches(self):
        c1 = Component(id='1')
        c2 = Component(id='2', children=[c1])
        c3 = Component(id='3')
        c4 = Component(id='4', children=[c3])
        c5 = Component(children=[c2, c4])
        self.assertEqual(c2['1'], c1)
        self.assertEqual(c4['3'], c3)
        self.assertEqual(c5['2'], c2)
        self.assertEqual(c5['4'], c4)
        self.assertEqual(c5['1'], c1)
        self.assertEqual(c5['3'], c3)

    def test_get_item_with_nested_children_with_mixed_strings_and_without_lists(self):  # noqa: E501
        c, c1, c2, c3, c4, c5 = nested_tree()
        self.assertEqual(
            list(c.keys()),
            [
                '0.0',
                '0.1',
                '0.1.x',
                '0.1.x.x',
                '0.1.x.x.0'
            ]
        )

        # Try to get each item
        for comp in [c1, c2, c3, c4, c5]:
            self.assertEqual(c[comp.id], comp)

        # Get an item that doesn't exist
        with self.assertRaises(KeyError):
            c['x']

    def test_len_with_nested_children_with_mixed_strings_and_without_lists(self):  # noqa: E501
        c = nested_tree()[0]
        self.assertEqual(
            len(c),
            5 +  # 5 components
            5 +  # c2 has 2 strings, 2 numbers, and a None
            1    # c1 has 1 string
        )

    def test_set_item_with_nested_children_with_mixed_strings_and_without_lists(self):  # noqa: E501
        keys = [
            '0.0',
            '0.1',
            '0.1.x',
            '0.1.x.x',
            '0.1.x.x.0'
        ]
        c = nested_tree()[0]

        # Test setting items starting from the innermost item
        for key in reversed(keys):
            new_id = 'new {}'.format(key)
            new_component = Component(
                id=new_id,
                children='new string'
            )
            c[key] = new_component
            self.assertEqual(c[new_id], new_component)

    def test_del_item_with_nested_children_with_mixed_strings_and_without_lists(self):  # noqa: E501
        c = nested_tree()[0]
        for key in reversed(list(c.keys())):
            c[key]
            del c[key]
            with self.assertRaises(KeyError):
                c[key]

    def test_traverse_with_nested_children_with_mixed_strings_and_without_lists(self):  # noqa: E501
        c, c1, c2, c3, c4, c5 = nested_tree()
        elements = [i for i in c.traverse()]
        self.assertEqual(
            elements,
            c.children + [c3] + [c2] + c2.children
        )

    def test_iter_with_nested_children_with_mixed_strings_and_without_lists(self):  # noqa: E501
        c = nested_tree()[0]
        keys = list(c.keys())
        # get a list of ids that __iter__ provides
        iter_keys = [i for i in c]
        self.assertEqual(keys, iter_keys)

    def test_to_plotly_json_with_nested_children_with_mixed_strings_and_without_lists(self):  # noqa: E501
        c = nested_tree()[0]
        Component._namespace
        Component._type

        self.assertEqual(json.loads(json.dumps(
            c.to_plotly_json(),
            cls=plotly.utils.PlotlyJSONEncoder
            )), {
                'type': 'TestComponent',
                'namespace': 'test_namespace',
                'props': {
                    'children': [
                        {
                            'type': 'TestComponent',
                            'namespace': 'test_namespace',
                            'props': {
                                'id': '0.0'
                            }
                        },
                        {
                            'type': 'TestComponent',
                            'namespace': 'test_namespace',
                            'props': {
                                'children': {
                                    'type': 'TestComponent',
                                    'namespace': 'test_namespace',
                                    'props': {
                                        'children': {
                                            'type': 'TestComponent',
                                            'namespace': 'test_namespace',
                                            'props': {
                                                'children': [
                                                    10,
                                                    None,
                                                    'wrap string',
                                                    {
                                                        'type': 'TestComponent',
                                                        'namespace': 'test_namespace',  # noqa: E501
                                                        'props': {
                                                            'children': 'string',
                                                            'id': '0.1.x.x.0'
                                                        }
                                                    },
                                                    'another string',
                                                    4.51
                                                ],
                                                'id': '0.1.x.x'
                                            }
                                        },
                                        'id': '0.1.x'
                                    }
                                },
                                'id': '0.1'
                            }
                        }
                    ],
                    'id': '0'
                }
            })

    def test_get_item_raises_key_if_id_doesnt_exist(self):
        c = Component()
        with self.assertRaises(KeyError):
            c['1']

        c1 = Component(id='1')
        with self.assertRaises(KeyError):
            c1['1']

        c2 = Component(id='2', children=[c1])
        with self.assertRaises(KeyError):
            c2['0']

        c3 = Component(children='string with no id')
        with self.assertRaises(KeyError):
            c3['0']

    def test_equality(self):
        # TODO - Why is this the case? How is == being performed?
        # __eq__ only needs __getitem__, __iter__, and __len__
        self.assertTrue(Component() == Component())
        self.assertTrue(Component() is not Component())

        c1 = Component(id='1')
        c2 = Component(id='2', children=[Component()])
        self.assertTrue(c1 == c2)
        self.assertTrue(c1 is not c2)

    def test_set_item(self):
        c1a = Component(id='1', children='Hello world')
        c2 = Component(id='2', children=c1a)
        self.assertEqual(c2['1'], c1a)
        c1b = Component(id='1', children='Brave new world')
        c2['1'] = c1b
        self.assertEqual(c2['1'], c1b)

    def test_set_item_with_children_as_list(self):
        c1 = Component(id='1')
        c2 = Component(id='2', children=[c1])
        self.assertEqual(c2['1'], c1)
        c3 = Component(id='3')
        c2['1'] = c3
        self.assertEqual(c2['3'], c3)

    def test_set_item_with_nested_children(self):
        c1 = Component(id='1')
        c2 = Component(id='2', children=[c1])
        c3 = Component(id='3')
        c4 = Component(id='4', children=[c3])
        c5 = Component(id='5', children=[c2, c4])

        c3b = Component(id='3')
        self.assertEqual(c5['3'], c3)
        self.assertTrue(c5['3'] is not '3')
        self.assertTrue(c5['3'] is not c3b)

        c5['3'] = c3b
        self.assertTrue(c5['3'] is c3b)
        self.assertTrue(c5['3'] is not c3)

        c2b = Component(id='2')
        c5['2'] = c2b
        self.assertTrue(c5['4'] is c4)
        self.assertTrue(c5['2'] is not c2)
        self.assertTrue(c5['2'] is c2b)
        with self.assertRaises(KeyError):
            c5['1']

    def test_set_item_raises_key_error(self):
        c1 = Component(id='1')
        c2 = Component(id='2', children=[c1])
        with self.assertRaises(KeyError):
            c2['3'] = Component(id='3')

    def test_del_item_from_list(self):
        c1 = Component(id='1')
        c2 = Component(id='2')
        c3 = Component(id='3', children=[c1, c2])
        self.assertEqual(c3['1'], c1)
        self.assertEqual(c3['2'], c2)
        del c3['2']
        with self.assertRaises(KeyError):
            c3['2']
        self.assertEqual(c3.children, [c1])

        del c3['1']
        with self.assertRaises(KeyError):
            c3['1']
        self.assertEqual(c3.children, [])

    def test_del_item_from_class(self):
        c1 = Component(id='1')
        c2 = Component(id='2', children=c1)
        self.assertEqual(c2['1'], c1)
        del c2['1']
        with self.assertRaises(KeyError):
            c2['1']

        self.assertEqual(c2.children, None)

    def test_to_plotly_json_without_children(self):
        c = Component(id='a')
        c._prop_names = ('id',)
        c._type = 'MyComponent'
        c._namespace = 'basic'
        self.assertEqual(
            c.to_plotly_json(),
            {'namespace': 'basic', 'props': {'id': 'a'}, 'type': 'MyComponent'}
        )

    def test_to_plotly_json_with_null_arguments(self):
        c = Component(id='a')
        c._prop_names = ('id', 'style',)
        c._type = 'MyComponent'
        c._namespace = 'basic'
        self.assertEqual(
            c.to_plotly_json(),
            {'namespace': 'basic', 'props': {'id': 'a'}, 'type': 'MyComponent'}
        )

        c = Component(id='a', style=None)
        c._prop_names = ('id', 'style',)
        c._type = 'MyComponent'
        c._namespace = 'basic'
        self.assertEqual(
            c.to_plotly_json(),
            {
                'namespace': 'basic', 'props': {'id': 'a', 'style': None},
                'type': 'MyComponent'
            }
        )

    def test_to_plotly_json_with_children(self):
        c = Component(id='a', children='Hello World')
        c._prop_names = ('id', 'children',)
        c._type = 'MyComponent'
        c._namespace = 'basic'
        self.assertEqual(
            c.to_plotly_json(),
            {
                'namespace': 'basic',
                'props': {
                    'id': 'a',
                    # TODO - Rename 'children' to 'children'
                    'children': 'Hello World'
                },
                'type': 'MyComponent'
            }
        )

    def test_to_plotly_json_with_nested_children(self):
        c1 = Component(id='1', children='Hello World')
        c1._prop_names = ('id', 'children',)
        c1._type = 'MyComponent'
        c1._namespace = 'basic'

        c2 = Component(id='2', children=c1)
        c2._prop_names = ('id', 'children',)
        c2._type = 'MyComponent'
        c2._namespace = 'basic'

        c3 = Component(id='3', children='Hello World')
        c3._prop_names = ('id', 'children',)
        c3._type = 'MyComponent'
        c3._namespace = 'basic'

        c4 = Component(id='4', children=[c2, c3])
        c4._prop_names = ('id', 'children',)
        c4._type = 'MyComponent'
        c4._namespace = 'basic'

        def to_dict(id, children):
            return {
                'namespace': 'basic',
                'props': {
                    'id': id,
                    'children': children
                },
                'type': 'MyComponent'
            }

        """
        self.assertEqual(
            json.dumps(c4.to_plotly_json(),
                       cls=plotly.utils.PlotlyJSONEncoder),
            json.dumps(to_dict('4', [
                to_dict('2', to_dict('1', 'Hello World')),
                to_dict('3', 'Hello World')
            ]))
        )
        """

    def test_to_plotly_json_with_wildcards(self):
        c = Component(id='a', **{'aria-expanded': 'true',
                                 'data-toggle': 'toggled',
                                 'data-none': None})
        c._prop_names = ('id',)
        c._type = 'MyComponent'
        c._namespace = 'basic'
        self.assertEqual(
            c.to_plotly_json(),
            {'namespace': 'basic',
             'props': {
                 'aria-expanded': 'true',
                 'data-toggle': 'toggled',
                 'data-none': None,
                 'id': 'a',
             },
             'type': 'MyComponent'}
        )

    def test_len(self):
        self.assertEqual(len(Component()), 0)
        self.assertEqual(len(Component(children='Hello World')), 1)
        self.assertEqual(len(Component(children=Component())), 1)
        self.assertEqual(len(Component(children=[Component(), Component()])),
                         2)
        self.assertEqual(len(Component(children=[
            Component(children=Component()),
            Component()
        ])), 3)

    def test_iter(self):
        # keys, __contains__, items, values, and more are all mixin methods
        # that we get for free by inheriting from the MutableMapping
        # and behave as according to our implementation of __iter__

        c = Component(
            id='1',
            children=[
                Component(id='2', children=[
                    Component(id='3', children=Component(id='4'))
                ]),
                Component(id='5', children=[
                    Component(id='6', children='Hello World')
                ]),
                Component(),
                Component(children='Hello World'),
                Component(children=Component(id='7')),
                Component(children=[Component(id='8')]),
            ]
        )
        # test keys()
        keys = [k for k in list(c.keys())]
        self.assertEqual(keys, ['2', '3', '4', '5', '6', '7', '8'])
        self.assertEqual([i for i in c], keys)

        # test values()
        components = [i for i in list(c.values())]
        self.assertEqual(components, [c[k] for k in keys])

        # test __iter__()
        for k in keys:
            # test __contains__()
            self.assertTrue(k in c)

        # test __items__
        items = [i for i in list(c.items())]
        self.assertEqual(list(zip(keys, components)), items)

    def test_pop(self):
        c2 = Component(id='2')
        c = Component(id='1', children=c2)
        c2_popped = c.pop('2')
        self.assertTrue('2' not in c)
        self.assertTrue(c2_popped is c2)


class TestGenerateClassFile(unittest.TestCase):
    def setUp(self):
        json_path = os.path.join('tests', 'development', 'metadata_test.json')
        with open(json_path) as data_file:
            json_string = data_file.read()
            data = json\
                .JSONDecoder(object_pairs_hook=collections.OrderedDict)\
                .decode(json_string)
            self.data = data

        # Create a folder for the new component file
        os.makedirs('TableComponents')

        # Import string not included in generated class string
        import_string =\
            "# AUTO GENERATED FILE - DO NOT EDIT\n\n" + \
            "from dash.development.base_component import" + \
            " Component, _explicitize_args\n\n\n"

        # Class string generated from generate_class_string
        self.component_class_string = import_string + generate_class_string(
            typename='Table',
            props=data['props'],
            description=data['description'],
            namespace='TableComponents'
        )

        # Class string written to file
        generate_class_file(
            typename='Table',
            props=data['props'],
            description=data['description'],
            namespace='TableComponents'
        )
        written_file_path = os.path.join(
            'TableComponents', "Table.py"
        )
        with open(written_file_path, 'r') as f:
            self.written_class_string = f.read()

        # The expected result for both class string and class file generation
        expected_string_path = os.path.join(
            'tests', 'development', 'metadata_test.py'
        )
        with open(expected_string_path, 'r') as f:
            self.expected_class_string = f.read()

    def tearDown(self):
        shutil.rmtree('TableComponents')

    def test_class_string(self):
        self.assertEqual(
            self.expected_class_string,
            self.component_class_string
        )

    def test_class_file(self):
        self.assertEqual(
            self.expected_class_string,
            self.written_class_string
        )


class TestGenerateClass(unittest.TestCase):
    def setUp(self):
        path = os.path.join('tests', 'development', 'metadata_test.json')
        with open(path) as data_file:
            json_string = data_file.read()
            data = json\
                .JSONDecoder(object_pairs_hook=collections.OrderedDict)\
                .decode(json_string)
            self.data = data

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

    def test_to_plotly_json(self):
        c = self.ComponentClass()
        self.assertEqual(c.to_plotly_json(), {
            'namespace': 'TableComponents',
            'type': 'Table',
            'props': {
                'children': None
            }
        })

        c = self.ComponentClass(id='my-id')
        self.assertEqual(c.to_plotly_json(), {
            'namespace': 'TableComponents',
            'type': 'Table',
            'props': {
                'children': None,
                'id': 'my-id'
            }
        })

        c = self.ComponentClass(id='my-id', optionalArray=None)
        self.assertEqual(c.to_plotly_json(), {
            'namespace': 'TableComponents',
            'type': 'Table',
            'props': {
                'children': None,
                'id': 'my-id',
                'optionalArray': None
            }
        })

    def test_arguments_become_attributes(self):
        kwargs = {
            'id': 'my-id',
            'children': 'text children',
            'optionalArray': [[1, 2, 3]]
        }
        component_instance = self.ComponentClass(**kwargs)
        for k, v in list(kwargs.items()):
            self.assertEqual(getattr(component_instance, k), v)

    def test_repr_single_default_argument(self):
        c1 = self.ComponentClass('text children')
        c2 = self.ComponentClass(children='text children')
        self.assertEqual(
            repr(c1),
            "Table('text children')"
        )
        self.assertEqual(
            repr(c2),
            "Table('text children')"
        )

    def test_repr_single_non_default_argument(self):
        c = self.ComponentClass(id='my-id')
        self.assertEqual(
            repr(c),
            "Table(id='my-id')"
        )

    def test_repr_multiple_arguments(self):
        # Note how the order in which keyword arguments are supplied is
        # not always equal to the order in the repr of the component
        c = self.ComponentClass(id='my id', optionalArray=[1, 2, 3])
        self.assertEqual(
            repr(c),
            "Table(optionalArray=[1, 2, 3], id='my id')"
        )

    def test_repr_nested_arguments(self):
        c1 = self.ComponentClass(id='1')
        c2 = self.ComponentClass(id='2', children=c1)
        c3 = self.ComponentClass(children=c2)
        self.assertEqual(
            repr(c3),
            "Table(Table(children=Table(id='1'), id='2'))"
        )

    def test_repr_with_wildcards(self):
        c = self.ComponentClass(id='1', **{"data-one": "one",
                                           "aria-two": "two"})
        data_first = "Table(id='1', data-one='one', aria-two='two')"
        aria_first = "Table(id='1', aria-two='two', data-one='one')"
        repr_string = repr(c)
        if not (repr_string == data_first or repr_string == aria_first):
            raise Exception("%s\nDoes not equal\n%s\nor\n%s" %
                            (repr_string, data_first, aria_first))

    def test_docstring(self):
        assert_docstring(self.assertEqual, self.ComponentClass.__doc__)

    def test_events(self):
        self.assertEqual(
            self.ComponentClass().available_events,
            ['restyle', 'relayout', 'click']
        )

    # This one is kind of pointless now
    def test_call_signature(self):
        __init__func = self.ComponentClass.__init__
        # TODO: Will break in Python 3
        # http://stackoverflow.com/questions/2677185/
        self.assertEqual(
            inspect.getargspec(__init__func).args,
            ['self',
             'children',
             'optionalArray',
             'optionalBool',
             'optionalFunc',
             'optionalNumber',
             'optionalObject',
             'optionalString',
             'optionalSymbol',
             'optionalNode',
             'optionalElement',
             'optionalMessage',
             'optionalEnum',
             'optionalUnion',
             'optionalArrayOf',
             'optionalObjectOf',
             'optionalObjectWithShapeAndNestedDescription',
             'optionalAny',
             'customProp',
             'customArrayProp',
             'id'] if hasattr(inspect, 'signature') else []


        )
        self.assertEqual(
            inspect.getargspec(__init__func).varargs,
            None if hasattr(inspect, 'signature') else 'args'
        )
        self.assertEqual(
            inspect.getargspec(__init__func).keywords,
            'kwargs'
        )
        if hasattr(inspect, 'signature'):
            self.assertEqual(
                [str(x) for x in inspect.getargspec(__init__func).defaults],
                ['None'] + ['undefined'] * 19
            )

    def test_required_props(self):
        with self.assertRaises(Exception):
            self.ComponentClassRequired()
        self.ComponentClassRequired(id='test')
        with self.assertRaises(Exception):
            self.ComponentClassRequired(id='test', lahlah='test')
        with self.assertRaises(Exception):
            self.ComponentClassRequired(children='test')


class TestMetaDataConversions(unittest.TestCase):
    def setUp(self):
        path = os.path.join('tests', 'development', 'metadata_test.json')
        with open(path) as data_file:
            json_string = data_file.read()
            data = json\
                .JSONDecoder(object_pairs_hook=collections.OrderedDict)\
                .decode(json_string)
            self.data = data

        self.expected_arg_strings = OrderedDict([
            ['children',
             'a list of or a singular dash component, string or number'],

            ['optionalArray', 'list'],

            ['optionalBool', 'boolean'],

            ['optionalFunc', ''],

            ['optionalNumber', 'number'],

            ['optionalObject', 'dict'],

            ['optionalString', 'string'],

            ['optionalSymbol', ''],

            ['optionalElement', 'dash component'],

            ['optionalNode',
             'a list of or a singular dash component, string or number'],

            ['optionalMessage', ''],

            ['optionalEnum', 'a value equal to: \'News\', \'Photos\''],

            ['optionalUnion', 'string | number'],

            ['optionalArrayOf', 'list'],

            ['optionalObjectOf',
             'dict with strings as keys and values of type number'],

            ['optionalObjectWithShapeAndNestedDescription', '\n'.join([

                "dict containing keys 'color', 'fontSize', 'figure'.",
                "Those keys have the following types: ",
                "  - color (string; optional)",
                "  - fontSize (number; optional)",
                "  - figure (optional): Figure is a plotly graph object. figure has the following type: dict containing keys 'data', 'layout'.",  # noqa: E501
                "Those keys have the following types: ",
                "  - data (list; optional): data is a collection of traces",
                "  - layout (dict; optional): layout describes the rest of the figure"  # noqa: E501

            ])],

            ['optionalAny', 'boolean | number | string | dict | list'],

            ['customProp', ''],

            ['customArrayProp', 'list'],

            ['data-*', 'string'],

            ['aria-*', 'string'],

            ['in', 'string'],

            ['id', 'string'],

            ['dashEvents', "a value equal to: 'restyle', 'relayout', 'click'"]
        ])

    def test_docstring(self):
        docstring = create_docstring(
            'Table',
            self.data['props'],
            parse_events(self.data['props']),
            self.data['description'],
        )
        assert_docstring(self.assertEqual, docstring)

    def test_docgen_to_python_args(self):

        props = self.data['props']

        for prop_name, prop in list(props.items()):
            self.assertEqual(
                js_to_py_type(prop['type']),
                self.expected_arg_strings[prop_name]
            )


def assert_docstring(assertEqual, docstring):
    for i, line in enumerate(docstring.split('\n')):
        assertEqual(line, ([
            "A Table component.",
            "This is a description of the component.",
            "It's multiple lines long.",
            '',
            "Keyword arguments:",
            "- children (a list of or a singular dash component, string or number; optional)",  # noqa: E501
            "- optionalArray (list; optional): Description of optionalArray",
            "- optionalBool (boolean; optional)",
            "- optionalNumber (number; optional)",
            "- optionalObject (dict; optional)",
            "- optionalString (string; optional)",

            "- optionalNode (a list of or a singular dash component, "
            "string or number; optional)",

            "- optionalElement (dash component; optional)",
            "- optionalEnum (a value equal to: 'News', 'Photos'; optional)",
            "- optionalUnion (string | number; optional)",
            "- optionalArrayOf (list; optional)",

            "- optionalObjectOf (dict with strings as keys and values "
            "of type number; optional)",

            "- optionalObjectWithShapeAndNestedDescription (optional): . "
            "optionalObjectWithShapeAndNestedDescription has the "
            "following type: dict containing keys "
            "'color', 'fontSize', 'figure'.",

            "Those keys have the following types: ",
            "  - color (string; optional)",
            "  - fontSize (number; optional)",

            "  - figure (optional): Figure is a plotly graph object. "
            "figure has the following type: dict containing "
            "keys 'data', 'layout'.",

            "Those keys have the following types: ",
            "  - data (list; optional): data is a collection of traces",

            "  - layout (dict; optional): layout describes "
            "the rest of the figure",

            "- optionalAny (boolean | number | string | dict | "
            "list; optional)",

            "- customProp (optional)",
            "- customArrayProp (list; optional)",
            '- data-* (string; optional)',
            '- aria-* (string; optional)',
            '- in (string; optional)',
            '- id (string; optional)',
            '',
            "Available events: 'restyle', 'relayout', 'click'",
            '        '
            ])[i]
                   )


class TestFlowMetaDataConversions(unittest.TestCase):
    def setUp(self):
        path = os.path.join('tests', 'development', 'flow_metadata_test.json')
        with open(path) as data_file:
            json_string = data_file.read()
            data = json\
                .JSONDecoder(object_pairs_hook=collections.OrderedDict)\
                .decode(json_string)
            self.data = data

        self.expected_arg_strings = OrderedDict([
            ['children', 'a list of or a singular dash component, string or number'],

            ['requiredString', 'string'],

            ['optionalString', 'string'],

            ['optionalBoolean', 'boolean'],

            ['optionalFunc', ''],

            ['optionalNode', 'a list of or a singular dash component, string or number'],

            ['optionalArray', 'list'],

            ['requiredUnion', 'string | number'],

            ['optionalSignature(shape)', '\n'.join([

                "dict containing keys 'checked', 'children', 'customData', 'disabled', 'label', 'primaryText', 'secondaryText', 'style', 'value'.",
                "Those keys have the following types: ",
                "- checked (boolean; optional)",
                "- children (a list of or a singular dash component, string or number; optional)",
                "- customData (bool | number | str | dict | list; required): A test description",
                "- disabled (boolean; optional)",
                "- label (string; optional)",
                "- primaryText (string; required): Another test description",
                "- secondaryText (string; optional)",
                "- style (dict; optional)",
                "- value (bool | number | str | dict | list; required)"

            ])],

            ['requiredNested', '\n'.join([

                "dict containing keys 'customData', 'value'.",
                "Those keys have the following types: ",
                "- customData (required): . customData has the following type: dict containing keys 'checked', 'children', 'customData', 'disabled', 'label', 'primaryText', 'secondaryText', 'style', 'value'.",
                "  Those keys have the following types: ",
                "  - checked (boolean; optional)",
                "  - children (a list of or a singular dash component, string or number; optional)",
                "  - customData (bool | number | str | dict | list; required)",
                "  - disabled (boolean; optional)",
                "  - label (string; optional)",
                "  - primaryText (string; required)",
                "  - secondaryText (string; optional)",
                "  - style (dict; optional)",
                "  - value (bool | number | str | dict | list; required)",
                "- value (bool | number | str | dict | list; required)",

            ])],
        ])

    def test_docstring(self):
        docstring = create_docstring(
            'Flow_component',
            self.data['props'],
            parse_events(self.data['props']),
            self.data['description'],
        )
        assert_flow_docstring(self.assertEqual, docstring)

    def test_docgen_to_python_args(self):

        props = self.data['props']

        for prop_name, prop in list(props.items()):
            self.assertEqual(
                js_to_py_type(prop['flowType'], is_flow_type=True),
                self.expected_arg_strings[prop_name]
            )


def assert_flow_docstring(assertEqual, docstring):
    for i, line in enumerate(docstring.split('\n')):
        assertEqual(line, ([
            "A Flow_component component.",
            "This is a test description of the component.",
            "It's multiple lines long.",
            "",
            "Keyword arguments:",
            "- requiredString (string; required): A required string",
            "- optionalString (string; optional): A string that isn't required.",
            "- optionalBoolean (boolean; optional): A boolean test",

            "- optionalNode (a list of or a singular dash component, string or number; optional): "
            "A node test",

            "- optionalArray (list; optional): An array test with a particularly ",
            "long description that covers several lines. It includes the newline character ",
            "and should span 3 lines in total.",

            "- requiredUnion (string | number; required)",

            "- optionalSignature(shape) (optional): This is a test of an object's shape. "
            "optionalSignature(shape) has the following type: dict containing keys 'checked', "
            "'children', 'customData', 'disabled', 'label', 'primaryText', 'secondaryText', "
            "'style', 'value'.",

            "  Those keys have the following types: ",
            "  - checked (boolean; optional)",
            "  - children (a list of or a singular dash component, string or number; optional)",
            "  - customData (bool | number | str | dict | list; required): A test description",
            "  - disabled (boolean; optional)",
            "  - label (string; optional)",
            "  - primaryText (string; required): Another test description",
            "  - secondaryText (string; optional)",
            "  - style (dict; optional)",
            "  - value (bool | number | str | dict | list; required)",

            "- requiredNested (required): . requiredNested has the following type: dict containing "
            "keys 'customData', 'value'.",

            "  Those keys have the following types: ",

            "  - customData (required): . customData has the following type: dict containing "
            "keys 'checked', 'children', 'customData', 'disabled', 'label', 'primaryText', "
            "'secondaryText', 'style', 'value'.",

            "    Those keys have the following types: ",
            "    - checked (boolean; optional)",
            "    - children (a list of or a singular dash component, string or number; optional)",
            "    - customData (bool | number | str | dict | list; required)",
            "    - disabled (boolean; optional)",
            "    - label (string; optional)",
            "    - primaryText (string; required)",
            "    - secondaryText (string; optional)",
            "    - style (dict; optional)",
            "    - value (bool | number | str | dict | list; required)",
            "  - value (bool | number | str | dict | list; required)",
            "",
            "Available events: "
        ])[i]
                   )
