from dash.development.base_component import generate_class, Component
import dash
import inspect
import json
import plotly
import unittest


Component._prop_names = ('id', 'a', 'content', 'style', )

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
        self.ComponentClass = generate_class(
            typename='Table',
            component_arguments=(
                'content', 'id', 'rows'
            ),
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

        c = self.ComponentClass(id='my-id', rows=None)
        self.assertEqual(c.to_plotly_json(), {
            'namespace': 'TableComponents',
            'type': 'Table',
            'props': {
                'content': None,
                'id': 'my-id',
                'rows': None
            }
        })

    def test_arguments_become_attributes(self):
        kwargs = {
            'id': 'my-id',
            'content': 'text content',
            'rows': [[1, 2, 3]]
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
        c = self.ComponentClass(id='my id', rows=[1, 2, 3])
        self.assertEqual(
            repr(c),
            "Table(id='my id', rows=[1, 2, 3])"
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
        self.assertEqual(
            self.ComponentClass.__doc__,
            '\n'.join([
                'A Table component.',
                'Valid keys:',
                '- content',
                '- id',
                '- rows',
                '        '
            ])
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
