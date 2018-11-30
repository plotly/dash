import collections
import abc
import inspect
import sys
import pprint

import six

from ..exceptions import ComponentInitializationValidationError
from .._utils import _merge
from .validator import DashValidator, generate_validation_error_message
from ._all_keywords import kwlist

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
            if v
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


# pylint: disable=unused-argument
def generate_class_string(typename, props, description, namespace):
    """
    Dynamically generate class strings to have nicely formatted docstrings,
    keyword arguments, and repr

    Inspired by http://jameso.be/2013/08/06/namedtuple.html

    Parameters
    ----------
    typename
    props
    description
    namespace

    Returns
    -------
    string

    """
    # TODO _prop_names, _type, _namespace, available_events,
    # and available_properties
    # can be modified by a Dash JS developer via setattr
    # TODO - Tab out the repr for the repr of these components to make it
    # look more like a hierarchical tree
    # TODO - Include "description" "defaultValue" in the repr and docstring
    #
    # TODO - Handle "required"
    #
    # TODO - How to handle user-given `null` values? I want to include
    # an expanded docstring like Dropdown(value=None, id=None)
    # but by templating in those None values, I have no way of knowing
    # whether a property is None because the user explicitly wanted
    # it to be `null` or whether that was just the default value.
    # The solution might be to deal with default values better although
    # not all component authors will supply those.
    # pylint: disable=too-many-locals
    c = '''
schema = {schema}

class {typename}(Component):
    """{docstring}"""
    _schema = schema
    @_explicitize_args
    def __init__(self, {default_argtext}):
        self._prop_names = {list_of_valid_keys}
        self._type = '{typename}'
        self._namespace = '{namespace}'
        self._valid_wildcard_attributes =\
            {list_of_valid_wildcard_attr_prefixes}
        self.available_events = {events}
        self.available_properties = {list_of_valid_keys}
        self.available_wildcard_properties =\
            {list_of_valid_wildcard_attr_prefixes}

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {{k: _locals[k] for k in _explicit_args}}

        for k in {required_args}:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        args.pop('children', None)
        super({typename}, self).__init__({argtext})

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('{typename}(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                '{typename}(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
'''

    filtered_props = reorder_props(filter_props(props))
    # pylint: disable=unused-variable
    list_of_valid_wildcard_attr_prefixes = repr(parse_wildcards(props))
    # pylint: disable=unused-variable
    list_of_valid_keys = repr(list(map(str, filtered_props.keys())))
    # pylint: disable=unused-variable
    docstring = create_docstring(
        component_name=typename,
        props=filtered_props,
        events=parse_events(props),
        description=description).replace('\r\n', '\n')

    # pylint: disable=unused-variable
    events = '[' + ', '.join(parse_events(props)) + ']'
    prop_keys = list(props.keys())
    if 'children' in props:
        default_argtext = 'children=None, '
        argtext = 'children=children, **args'  # Children will be popped before
    else:
        default_argtext = ''
        argtext = '**args'
    for p in props.keys():
        if (
                not p.endswith("-*") and  # Not a wildcard attribute
                p not in kwlist and  # Not a protected keyword
                p not in ['dashEvents', 'fireEvent', 'setProps'] and
                p != 'children'  # Already accounted for
        ):
            default_argtext += ('{:s}=Component.REQUIRED, '.format(p)
                                if props[p]['required'] else
                                '{:s}=Component.UNDEFINED, '.format(p))
    default_argtext += '**kwargs'
    schema = {
        k: generate_property_schema(v)
        for k, v in props.items() if not k.endswith("-*")
    }
    required_args = required_props(props)
    return c.format(**locals())


# pylint: disable=unused-argument
def generate_class_file(typename, props, description, namespace):
    """
    Generate a python class file (.py) given a class string

    Parameters
    ----------
    typename
    props
    description
    namespace

    Returns
    -------

    """
    import_string =\
        "# AUTO GENERATED FILE - DO NOT EDIT\n\n" + \
        "from dash.development.base_component import " + \
        "Component, _explicitize_args\n\n\n"
    class_string = generate_class_string(
        typename,
        props,
        description,
        namespace
    )
    file_name = "{:s}.py".format(typename)

    file_path = os.path.join(namespace, file_name)
    with open(file_path, 'w') as f:
        f.write(import_string)
        f.write(class_string)


# pylint: disable=unused-argument
def generate_class(typename, props, description, namespace):
    """
    Generate a python class object given a class string

    Parameters
    ----------
    typename
    props
    description
    namespace

    Returns
    -------

    """
    string = generate_class_string(typename, props, description, namespace)
    scope = {'Component': Component, '_explicitize_args': _explicitize_args}
    # pylint: disable=exec-used
    exec(string, scope)
    result = scope[typename]
    return result


def required_props(props):
    """
    Pull names of required props from the props object

    Parameters
    ----------
    props: dict

    Returns
    -------
    list
        List of prop names (str) that are required for the Component
    """
    return [prop_name for prop_name, prop in list(props.items())
            if prop['required']]


def create_docstring(component_name, props, events, description):
    """
    Create the Dash component docstring

    Parameters
    ----------
    component_name: str
        Component name
    props: dict
        Dictionary with {propName: propMetadata} structure
    events: list
        List of Dash events
    description: str
        Component description

    Returns
    -------
    str
        Dash component docstring
    """
    # Ensure props are ordered with children first
    props = reorder_props(props=props)

    return (
        """A {name} component.\n{description}

Keyword arguments:\n{args}

Available events: {events}"""
    ).format(
        name=component_name,
        description=description,
        args='\n'.join(
            create_prop_docstring(
                prop_name=p,
                type_object=prop['type'] if 'type' in prop
                else prop['flowType'],
                required=prop['required'],
                description=prop['description'],
                indent_num=0,
                is_flow_type='flowType' in prop and 'type' not in prop)
            for p, prop in list(filter_props(props).items())),
        events=', '.join(events))


def parse_events(props):
    """
    Pull out the dashEvents from the Component props

    Parameters
    ----------
    props: dict
        Dictionary with {propName: propMetadata} structure

    Returns
    -------
    list
        List of Dash event strings
    """
    if 'dashEvents' in props and props['dashEvents']['type']['name'] == 'enum':
        events = [v['value'] for v in props['dashEvents']['type']['value']]
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
