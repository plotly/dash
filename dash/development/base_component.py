import collections
import abc
import inspect
import sys
import pprint

import six

from ..exceptions import ComponentInitializationValidationError
from .._utils import _merge
from .validator import DashValidator, generate_validation_error_message

_initialization_validation_error_callback = """
A Dash Component was initialized with invalid properties!

Dash tried to create a `{component_name}` component with the
following arguments, which caused a validation failure:

***************************************************************
{component_args}
***************************************************************

The expected schema for the `{component_name}` component is:

***************************************************************
{component_schema}
***************************************************************

The errors in validation are as follows:


"""


def _explicitize_args(func):
    # Python 2
    if hasattr(func, 'func_code'):
        varnames = func.func_code.co_varnames
    # Python 3
    else:
        varnames = func.__code__.co_varnames

    def wrapper(*args, **kwargs):
        if '_explicit_args' in kwargs.keys():
            raise Exception('Variable _explicit_args should not be set.')
        kwargs['_explicit_args'] = \
            list(
                set(
                    list(varnames[:len(args)]) + [k for k, _ in kwargs.items()]
                )
            )
        if 'self' in kwargs['_explicit_args']:
            kwargs['_explicit_args'].remove('self')
        return func(*args, **kwargs)

    # If Python 3, we can set the function signature to be correct
    if hasattr(inspect, 'signature'):
        # pylint: disable=no-member
        new_sig = inspect.signature(wrapper).replace(
            parameters=inspect.signature(func).parameters.values()
        )
        wrapper.__signature__ = new_sig
    return wrapper


# pylint: disable=no-init,too-few-public-methods
class ComponentRegistry:
    """Holds a registry of the namespaces used by components."""

    registry = set()
    __dist_cache = {}

    @classmethod
    def get_resources(cls, resource_name):
        cached = cls.__dist_cache.get(resource_name)

        if cached:
            return cached

        cls.__dist_cache[resource_name] = resources = []

        for module_name in cls.registry:
            module = sys.modules[module_name]
            resources.extend(getattr(module, resource_name, []))

        return resources


class ComponentMeta(abc.ABCMeta):

    # pylint: disable=arguments-differ
    def __new__(mcs, name, bases, attributes):
        component = abc.ABCMeta.__new__(mcs, name, bases, attributes)
        module = attributes['__module__'].split('.')[0]
        if name == 'Component' or module == 'builtins':
            # Don't do the base component
            # and the components loaded dynamically by load_component
            # as it doesn't have the namespace.
            return component

        ComponentRegistry.registry.add(module)

        return component


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def _check_if_has_indexable_children(item):
    if (not hasattr(item, 'children') or
            (not isinstance(item.children, Component) and
             not isinstance(item.children, (tuple,
                                            collections.MutableSequence)))):

        raise KeyError


@six.add_metaclass(ComponentMeta)
class Component(collections.MutableMapping):
    class _UNDEFINED(object):
        def __repr__(self):
            return 'undefined'

        def __str__(self):
            return 'undefined'

    UNDEFINED = _UNDEFINED()

    class _REQUIRED(object):
        def __repr__(self):
            return 'required'

        def __str__(self):
            return 'required'

    REQUIRED = _REQUIRED()

    _schema = {}

    def __init__(self, **kwargs):
        # pylint: disable=super-init-not-called
        for k, v in list(kwargs.items()):
            # pylint: disable=no-member
            k_in_propnames = k in self._prop_names
            k_in_wildcards = any([k.startswith(w)
                                  for w in
                                  self._valid_wildcard_attributes])
            if not k_in_propnames and not k_in_wildcards:
                raise TypeError(
                    'Unexpected keyword argument `{}`'.format(k) +
                    '\nAllowed arguments: {}'.format(
                        # pylint: disable=no-member
                        ', '.join(sorted(self._prop_names))
                    )
                )
            setattr(self, k, v)

    def to_plotly_json(self):
        # Add normal properties
        props = {
            p: getattr(self, p)
            for p in self._prop_names  # pylint: disable=no-member
            if hasattr(self, p)
        }
        # Add the wildcard properties data-* and aria-*
        props.update({
            k: getattr(self, k)
            for k in self.__dict__
            if any(k.startswith(w) for w in
                   self._valid_wildcard_attributes)  # pylint:disable=no-member
        })
        as_json = {
            'props': props,
            'type': self._type,  # pylint: disable=no-member
            'namespace': self._namespace  # pylint: disable=no-member
        }

        return as_json

    # pylint: disable=too-many-branches, too-many-return-statements
    # pylint: disable=redefined-builtin, inconsistent-return-statements
    def _get_set_or_delete(self, id, operation, new_item=None):
        _check_if_has_indexable_children(self)

        # pylint: disable=access-member-before-definition,
        # pylint: disable=attribute-defined-outside-init
        if isinstance(self.children, Component):
            if getattr(self.children, 'id', None) is not None:
                # Woohoo! It's the item that we're looking for
                if self.children.id == id:
                    if operation == 'get':
                        return self.children
                    elif operation == 'set':
                        self.children = new_item
                        return
                    elif operation == 'delete':
                        self.children = None
                        return

            # Recursively dig into its subtree
            try:
                if operation == 'get':
                    return self.children.__getitem__(id)
                elif operation == 'set':
                    self.children.__setitem__(id, new_item)
                    return
                elif operation == 'delete':
                    self.children.__delitem__(id)
                    return
            except KeyError:
                pass

        # if children is like a list
        if isinstance(self.children, (tuple, collections.MutableSequence)):
            for i, item in enumerate(self.children):
                # If the item itself is the one we're looking for
                if getattr(item, 'id', None) == id:
                    if operation == 'get':
                        return item
                    elif operation == 'set':
                        self.children[i] = new_item
                        return
                    elif operation == 'delete':
                        del self.children[i]
                        return

                # Otherwise, recursively dig into that item's subtree
                # Make sure it's not like a string
                elif isinstance(item, Component):
                    try:
                        if operation == 'get':
                            return item.__getitem__(id)
                        elif operation == 'set':
                            item.__setitem__(id, new_item)
                            return
                        elif operation == 'delete':
                            item.__delitem__(id)
                            return
                    except KeyError:
                        pass

        # The end of our branch
        # If we were in a list, then this exception will get caught
        raise KeyError(id)

    # Supply ABC methods for a MutableMapping:
    # - __getitem__
    # - __setitem__
    # - __delitem__
    # - __iter__
    # - __len__

    def __getitem__(self, id):  # pylint: disable=redefined-builtin
        """Recursively find the element with the given ID through the tree
        of children.
        """

        # A component's children can be undefined, a string, another component,
        # or a list of components.
        return self._get_set_or_delete(id, 'get')

    def __setitem__(self, id, item):  # pylint: disable=redefined-builtin
        """Set an element by its ID."""
        return self._get_set_or_delete(id, 'set', item)

    def __delitem__(self, id):  # pylint: disable=redefined-builtin
        """Delete items by ID in the tree of children."""
        return self._get_set_or_delete(id, 'delete')

    def traverse(self):
        """Yield each item in the tree."""
        for t in self.traverse_with_paths():
            yield t[1]

    def traverse_with_paths(self):
        """Yield each item with its path in the tree."""
        children = getattr(self, 'children', None)
        children_type = type(children).__name__
        children_id = "(id={:s})".format(children.id) \
                      if getattr(children, 'id', False) else ''
        children_string = children_type + ' ' + children_id

        # children is just a component
        if isinstance(children, Component):
            yield "[*] " + children_string, children
            for p, t in children.traverse_with_paths():
                yield "\n".join(["[*] " + children_string, p]), t

        # children is a list of components
        elif isinstance(children, (tuple, collections.MutableSequence)):
            for idx, i in enumerate(children):
                list_path = "[{:d}] {:s} {}".format(
                    idx,
                    type(i).__name__,
                    "(id={:s})".format(i.id) if getattr(i, 'id', False) else ''
                )
                yield list_path, i

                if isinstance(i, Component):
                    for p, t in i.traverse_with_paths():
                        yield "\n".join([list_path, p]), t

    def validate(self):
        # Make sure arguments have valid values
        DashValidator.set_component_class(Component)
        validator = DashValidator(
            self._schema,
            allow_unknown=True,
        )
        # pylint: disable=no-member
        args = {
            k: v
            for k, v in ((x, getattr(self, x, None)) for x in self._prop_names)
            if v is not None
        }
        valid = validator.validate(args)
        if not valid:
            # pylint: disable=protected-access
            error_message = _initialization_validation_error_callback.format(
                component_name=self.__class__.__name__,
                component_args=pprint.pformat(args),
                component_schema=pprint.pformat(self.__class__._schema)
            )

            raise ComponentInitializationValidationError(
                generate_validation_error_message(
                    validator.errors,
                    0,
                    error_message
                )
            )

    def __iter__(self):
        """Yield IDs in the tree of children."""
        for t in self.traverse():
            if (isinstance(t, Component) and
                    getattr(t, 'id', None) is not None):

                yield t.id

    def __len__(self):
        """Return the number of items in the tree."""
        # TODO - Should we return the number of items that have IDs
        # or just the number of items?
        # The number of items is more intuitive but returning the number
        # of IDs matches __iter__ better.
        length = 0
        if getattr(self, 'children', None) is None:
            length = 0
        elif isinstance(self.children, Component):
            length = 1
            length += len(self.children)
        elif isinstance(self.children, (tuple, collections.MutableSequence)):
            for c in self.children:
                length += 1
                if isinstance(c, Component):
                    length += len(c)
        else:
            # string or number
            length = 1
        return length


def schema_is_nullable(type_object):
    if type_object and 'name' in type_object:
        if type_object['name'] == 'enum':
            values = type_object['value']
            for v in values:
                value = v['value']
                if value == 'null':
                    return True
        elif type_object['name'] == 'union':
            values = type_object['value']
            if any(schema_is_nullable(v) for v in values):
                return True
    return False


def js_to_cerberus_type(type_object):
    def _enum(x):
        schema = {'allowed': [],
                  'type': ('string', 'number')}
        values = x['value']
        for v in values:
            value = v['value']
            if value == 'null':
                schema['nullable'] = True
                schema['allowed'].append(None)
            elif value == 'true':
                schema['allowed'].append(True)
            elif value == 'false':
                schema['allowed'].append(False)
            else:
                string_value = v['value'].strip("'\"'")
                schema['allowed'].append(string_value)
                try:
                    int_value = int(string_value)
                    schema['allowed'].append(int_value)
                except ValueError:
                    pass
                try:
                    float_value = float(string_value)
                    schema['allowed'].append(float_value)
                except ValueError:
                    pass
        return schema

    converters = {
        'None': lambda x: {},
        'func': lambda x: {},
        'symbol': lambda x: {},
        'custom': lambda x: {},
        'node': lambda x: {
            'anyof': [
                {'type': 'component'},
                {'type': 'boolean'},
                {'type': 'number'},
                {'type': 'string'},
                {
                    'type': 'list',
                    'schema': {
                        'type': (
                            'component',
                            'boolean',
                            'number',
                            'string')
                    }
                }
            ]
        },
        'element': lambda x: {'type': 'component'},
        'enum': _enum,
        'union': lambda x: {
            'anyof': [js_to_cerberus_type(v) for v in x['value']],
        },
        'any': lambda x: {},  # Empty means no validation is run
        'string': lambda x: {'type': 'string'},
        'bool': lambda x: {'type': 'boolean'},
        'number': lambda x: {'type': 'number'},
        'integer': lambda x: {'type': 'number'},
        'object': lambda x: {'type': 'dict'},
        'objectOf': lambda x: {
            'type': 'dict',
            'nullable': schema_is_nullable(x),
            'valueschema': js_to_cerberus_type(x['value'])
        },
        'array': lambda x: {'type': 'list'},
        'arrayOf': lambda x: {
            'type': 'list',
            'schema': _merge(
                js_to_cerberus_type(x['value']),
                {'nullable': schema_is_nullable(x['value'])}
            )
        },
        'shape': lambda x: {
            'type': 'dict',
            'allow_unknown': False,
            'nullable': schema_is_nullable(x),
            'schema': {
                k: js_to_cerberus_type(v) for k, v in x['value'].items()
            }
        },
        'instanceOf': lambda x: dict(
            Date={'type': 'datetime'},
        ).get(x['value'], {})
    }
    if type_object:
        converter = converters[type_object.get('name', 'None')]
        schema = converter(type_object)
        return schema
    return {}


def generate_property_schema(jsonSchema):
    schema = {}
    type_object = jsonSchema.get('type', None)
    required = jsonSchema.get('required', None)
    propType = js_to_cerberus_type(type_object)
    if propType:
        schema.update(propType)
    schema['nullable'] = schema_is_nullable(type_object)
    schema['required'] = required
    return schema
