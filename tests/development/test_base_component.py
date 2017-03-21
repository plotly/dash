from collections import OrderedDict
from dash.development.base_component import (
    generate_class,
    Component,
    js_to_py_type,
    create_docstring,
    parse_events
)
import dash
import inspect
import json
import plotly
import unittest
import collections
import json
import os


Component._prop_names = ('id', 'a', 'content', 'style', )
Component._type = 'TestComponent'
Component._namespace = 'test_namespace'


def nested_tree():
    '''This tree has a few unique properties:
    - Content is mixed strings and components (as in c2)
    - Content is just components (as in c)
    - Content is just strings (as in c1)
    - Content is just a single component (as in c3, c4)
    - Content contains numbers (as in c2)
    - Content contains "None" items (as in c2)
    '''
    c1 = Component(
        id='0.1.x.x.0',
        content='string'
    )
    c2 = Component(
        id='0.1.x.x',
        content=[10, None, 'wrap string', c1, 'another string', 4.51]
    )
    c3 = Component(
        id='0.1.x',
        # content is just a component
        content=c2
    )
    c4 = Component(
        id='0.1',
        content=c3
    )
    c5 = Component(id='0.0')
    c = Component(id='0', content=[c5, c4])
    return c, c1, c2, c3, c4, c5


class TestComponent(unittest.TestCase):
    def test_init(self):
        c = Component(a=3)

    def test_get_item_with_content(self):
        c1 = Component(id='1')
        c2 = Component(content=[c1])
        self.assertEqual(c2['1'], c1)

    def test_get_item_with_content_as_component_instead_of_list(self):
        c1 = Component(id='1')
        c2 = Component(id='2', content=c1)
        self.assertEqual(c2['1'], c1)

    def test_get_item_with_nested_content_one_branch(self):
        c1 = Component(id='1')
        c2 = Component(id='2', content=[c1])
        c3 = Component(content=[c2])
        self.assertEqual(c2['1'], c1)
        self.assertEqual(c3['2'], c2)
        self.assertEqual(c3['1'], c1)

    def test_get_item_with_nested_content_two_branches(self):
        c1 = Component(id='1')
        c2 = Component(id='2', content=[c1])
        c3 = Component(id='3')
        c4 = Component(id='4', content=[c3])
        c5 = Component(content=[c2, c4])
        self.assertEqual(c2['1'], c1)
        self.assertEqual(c4['3'], c3)
        self.assertEqual(c5['2'], c2)
        self.assertEqual(c5['4'], c4)
        self.assertEqual(c5['1'], c1)
        self.assertEqual(c5['3'], c3)

    def test_get_item_with_nested_content_with_mixed_strings_and_without_lists(self):
        c, c1, c2, c3, c4, c5 = nested_tree()
        self.assertEqual(
            c.keys(),
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

    def test_len_with_nested_content_with_mixed_strings_and_without_lists(self):
        c = nested_tree()[0]
        self.assertEqual(
            len(c),
            5 + # 5 components
            5 + # c2 has 2 strings, 2 numbers, and a None
            1# c1 has 1 string
        )

    def test_set_item_with_nested_content_with_mixed_strings_and_without_lists(self):
        keys = [
            '0.0',
            '0.1',
            '0.1.x',
            '0.1.x.x',
            '0.1.x.x.0'
        ]
        c = nested_tree()[0]

        # Test setting items starting from the innermost item
        for i, key in enumerate(reversed(keys)):
            new_id = 'new {}'.format(key)
            new_component = Component(
                id=new_id,
                content='new string'
            )
            c[key] = new_component
            self.assertEqual(c[new_id], new_component)

    def test_del_item_with_nested_content_with_mixed_strings_and_without_lists(self):
        c = nested_tree()[0]
        for key in reversed(c.keys()):
            c[key]
            del c[key]
            with self.assertRaises(KeyError):
                c[key]

    def test_traverse_with_nested_content_with_mixed_strings_and_without_lists(self):
        c, c1, c2, c3, c4, c5 = nested_tree()
        elements = [i for i in c.traverse()]
        self.assertEqual(
            elements,
            c.content + [c3] + [c2] + c2.content
        )

    def test_iter_with_nested_content_with_mixed_strings_and_without_lists(self):
        c = nested_tree()[0]
        keys = c.keys()
        # get a list of ids that __iter__ provides
        iter_keys = [i for i in c]
        self.assertEqual(keys, iter_keys)

    def test_to_plotly_json_with_nested_content_with_mixed_strings_and_without_lists(self):
        c = nested_tree()[0]
        n = Component._namespace
        t = Component._type

        self.assertEqual(json.loads(json.dumps(
                c.to_plotly_json(),
                cls=plotly.utils.PlotlyJSONEncoder
            )), {
            'type': 'TestComponent',
            'namespace': 'test_namespace',
            'props': {
                'content': [
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
                            'content': {
                                'type': 'TestComponent',
                                'namespace': 'test_namespace',
                                'props': {
                                    'content': {
                                        'type': 'TestComponent',
                                        'namespace': 'test_namespace',
                                        'props': {
                                            'content': [
                                                10,
                                                None,
                                                'wrap string',
                                                {
                                                    'type': 'TestComponent',
                                                    'namespace': 'test_namespace',
                                                    'props': {
                                                        'content': 'string',
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

        c2 = Component(id='2', content=[c1])
        with self.assertRaises(KeyError):
            c2['0']

        c3 = Component(content='string with no id')
        with self.assertRaises(KeyError):
            c3['0']

    def test_equality(self):
        # TODO - Why is this the case? How is == being performed?
        # __eq__ only needs __getitem__, __iter__, and __len__
        self.assertTrue(Component() == Component())
        self.assertTrue(Component() is not Component())

        c1 = Component(id='1')
        c2 = Component(id='2', content=[Component()])
        self.assertTrue(c1 == c2)
        self.assertTrue(c1 is not c2)

    def test_set_item(self):
        c1a = Component(id='1', content='Hello world')
        c2 = Component(id='2', content=c1a)
        self.assertEqual(c2['1'], c1a)
        c1b = Component(id='1', content='Brave new world')
        c2['1'] = c1b
        self.assertEqual(c2['1'], c1b)

    def test_set_item_with_content_as_list(self):
        c1 = Component(id='1')
        c2 = Component(id='2', content=[c1])
        self.assertEqual(c2['1'], c1)
        c3 = Component(id='3')
        c2['1'] = c3
        self.assertEqual(c2['3'], c3)

    def test_set_item_with_nested_content(self):
        c1 = Component(id='1')
        c2 = Component(id='2', content=[c1])
        c3 = Component(id='3')
        c4 = Component(id='4', content=[c3])
        c5 = Component(id='5', content=[c2, c4])

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
        c2 = Component(id='2', content=[c1])
        with self.assertRaises(KeyError):
            c2['3'] = Component(id='3')

    def test_del_item_from_list(self):
        c1 = Component(id='1')
        c2 = Component(id='2')
        c3 = Component(id='3', content=[c1, c2])
        self.assertEqual(c3['1'], c1)
        self.assertEqual(c3['2'], c2)
        del c3['2']
        with self.assertRaises(KeyError):
            c3['2']
        self.assertEqual(c3.content, [c1])

        del c3['1']
        with self.assertRaises(KeyError):
            c3['1']
        self.assertEqual(c3.content, [])

    def test_del_item_from_class(self):
        c1 = Component(id='1')
        c2 = Component(id='2', content=c1)
        self.assertEqual(c2['1'], c1)
        del c2['1']
        with self.assertRaises(KeyError):
            c2['1']

        self.assertEqual(c2.content, None)

    def test_to_plotly_json_without_content(self):
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

    def test_to_plotly_json_with_content(self):
        c = Component(id='a', content='Hello World')
        c._prop_names = ('id', 'content',)
        c._type = 'MyComponent'
        c._namespace = 'basic'
        self.assertEqual(
            c.to_plotly_json(),
            {
                'namespace': 'basic',
                'props': {
                    'id': 'a',
                    # TODO - Rename 'content' to 'children'
                    'content': 'Hello World'
                },
                'type': 'MyComponent'
            }
        )

    def test_to_plotly_json_with_nested_content(self):
        c1 = Component(id='1', content='Hello World')
        c1._prop_names = ('id', 'content',)
        c1._type = 'MyComponent'
        c1._namespace = 'basic'

        c2 = Component(id='2', content=c1)
        c2._prop_names = ('id', 'content',)
        c2._type = 'MyComponent'
        c2._namespace = 'basic'

        c3 = Component(id='3', content='Hello World')
        c3._prop_names = ('id', 'content',)
        c3._type = 'MyComponent'
        c3._namespace = 'basic'

        c4 = Component(id='4', content=[c2, c3])
        c4._prop_names = ('id', 'content',)
        c4._type = 'MyComponent'
        c4._namespace = 'basic'

        def to_dict(id, content):
            return {
                'namespace': 'basic',
                'props': {
                    'id': id,
                    'content': content
                },
                'type': 'MyComponent'
            }

        self.assertEqual(
            json.dumps(c4.to_plotly_json(),
                       cls=plotly.utils.PlotlyJSONEncoder),
            json.dumps(to_dict('4', [
                to_dict('2', to_dict('1', 'Hello World')),
                to_dict('3', 'Hello World')
            ]))
        )

    def test_len(self):
        self.assertEqual(len(Component()), 0)
        self.assertEqual(len(Component(content='Hello World')), 1)
        self.assertEqual(len(Component(content=Component())), 1)
        self.assertEqual(len(Component(content=[Component(), Component()])), 2)
        self.assertEqual(len(Component(content=[
            Component(content=Component()),
            Component()
        ])), 3)

    def test_iter(self):
        # keys, __contains__, items, values, and more are all mixin methods
        # that we get for free by inheriting from the MutableMapping
        # and behave as according to our implementation of __iter__

        c = Component(
            id='1',
            content=[
                Component(id='2', content=[
                    Component(id='3', content=Component(id='4'))
                ]),
                Component(id='5', content=[
                    Component(id='6', content='Hello World')
                ]),
                Component(),
                Component(content='Hello World'),
                Component(content=Component(id='7')),
                Component(content=[Component(id='8')]),
            ]
        )
        # test keys()
        keys = [k for k in c.keys()]
        self.assertEqual(keys, ['2', '3', '4', '5', '6', '7', '8'])
        self.assertEqual([i for i in c], keys)

        # test values()
        components = [i for i in c.values()]
        self.assertEqual(components, [c[k] for k in keys])

        # test __iter__()
        for k in keys:
            # test __contains__()
            self.assertTrue(k in c)

        # test __items__
        items = [i for i in c.items()]
        self.assertEqual(zip(keys, components), items)

    def test_pop(self):
        c2 = Component(id='2')
        c = Component(id='1', content=c2)
        c2_popped = c.pop('2')
        self.assertTrue('2' not in c)
        self.assertTrue(c2_popped is c2)


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

    def test_to_plotly_json(self):
        c = self.ComponentClass()
        self.assertEqual(c.to_plotly_json(), {
            'namespace': 'TableComponents',
            'type': 'Table',
            'props': {
                'content': None
            }
        })

        c = self.ComponentClass(id='my-id')
        self.assertEqual(c.to_plotly_json(), {
            'namespace': 'TableComponents',
            'type': 'Table',
            'props': {
                'content': None,
                'id': 'my-id'
            }
        })

        c = self.ComponentClass(id='my-id', optionalArray=None)
        self.assertEqual(c.to_plotly_json(), {
            'namespace': 'TableComponents',
            'type': 'Table',
            'props': {
                'content': None,
                'id': 'my-id',
                'optionalArray': None
            }
        })

    def test_arguments_become_attributes(self):
        kwargs = {
            'id': 'my-id',
            'content': 'text content',
            'optionalArray': [[1, 2, 3]]
        }
        component_instance = self.ComponentClass(**kwargs)
        for k, v in kwargs.iteritems():
            self.assertEqual(getattr(component_instance, k), v)

    def test_repr_single_default_argument(self):
        c1 = self.ComponentClass('text content')
        c2 = self.ComponentClass(content='text content')
        self.assertEqual(
            repr(c1),
            "Table('text content')"
        )
        self.assertEqual(
            repr(c2),
            "Table('text content')"
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
        c2 = self.ComponentClass(id='2', content=c1)
        c3 = self.ComponentClass(content=c2)
        self.assertEqual(
            repr(c3),
            "Table(Table(content=Table(id='1'), id='2'))"
        )

    def test_docstring(self):
        assert_docstring(self.assertEqual, self.ComponentClass.__doc__)

    def test_events(self):
        self.assertEqual(
            self.ComponentClass()._events,
            ['restyle', 'relayout', 'click']
        )

    def test_call_signature(self):
        # TODO: Will break in Python 3
        # http://stackoverflow.com/questions/2677185/
        self.assertEqual(
            inspect.getargspec(self.ComponentClass.__init__).args,
            ['self', 'content']
        )
        self.assertEqual(
            inspect.getargspec(self.ComponentClass.__init__).defaults,
            (None, )
        )


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
            ['content', 'a list of or a singular dash component, string or number'],

            ['optionalArray', 'list'],

            ['optionalBool', 'boolean'],

            ['optionalFunc', ''],

            ['optionalNumber', 'number'],

            ['optionalObject', 'dict'],

            ['optionalString', 'string'],

            ['optionalSymbol', ''],

            ['optionalElement', 'dash component'],

            ['optionalNode', 'a list of or a singular dash component, string or number'],

            ['optionalMessage', ''],

            ['optionalEnum', 'a value equal to: \'News\', \'Photos\''],

            ['optionalUnion', 'string | number'],

            ['optionalArrayOf', 'list'],

            ['optionalObjectOf', 'dict with strings as keys and values of type number'],

            ['optionalObjectWithShapeAndNestedDescription', '\n'.join([

                "dict containing keys 'color', 'fontSize', 'figure'.",
                "Those keys have the following types: ",
                "  - color (string; optional)",
                "  - fontSize (number; optional)",
                "  - figure (optional): Figure is a plotly graph object. figure has the following type: dict containing keys 'data', 'layout'.",
                "Those keys have the following types: ",
                "  - data (list; optional): data is a collection of traces",
                "  - layout (dict; optional): layout describes the rest of the figure"

            ])],

            ['requiredFunc', ''],

            ['requiredAny', 'boolean | number | string | dict | list'],

            ['requiredArray', 'list'],

            ['customProp', ''],

            ['customArrayProp', 'list'],

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

        for prop_name, prop in props.iteritems():
            self.assertEqual(
                js_to_py_type(prop['type']),
                self.expected_arg_strings[prop_name]
            )


def assert_docstring(assertEqual, docstring):
    for i, line in enumerate(docstring.split('\n')):
        assertEqual(
            line,
            ([
            "A Table component.",
            "This is a description of the component.",
            "It's multiple lines long.",
            '',
            "Keyword arguments:",
            "- content (a list of or a singular dash component, string or number; optional)",
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

            "- requiredAny (boolean | number | string | dict | "
            "list; required)",

            "- requiredArray (list; required)",
            "- customProp (optional)",
            "- customArrayProp (list; optional)",
            '- id (string; optional)',
            '',
            "Available events: 'restyle', 'relayout', 'click'",
            '        '
            ])[i]
        )
