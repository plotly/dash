import collections
import copy


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def _check_if_has_indexable_children(item):
    if (not hasattr(item, 'children') or
            (not isinstance(item.children, Component) and
             not isinstance(item.children, collections.MutableSequence))):

        raise KeyError


class Component(collections.MutableMapping):
    def __init__(self, **kwargs):
        # pylint: disable=super-init-not-called
        for k, v in list(kwargs.items()):
            if k not in self._prop_names:  # pylint: disable=no-member
                # TODO - What's the right exception here?
                # pylint: disable=no-member
                raise Exception(
                    'Unexpected keyword argument `{}`'.format(k) +
                    '\nAllowed arguments: {}'.format(
                        ', '.join(sorted(self._prop_names))
                    )
                )
            setattr(self, k, v)

    def to_plotly_json(self):
        as_json = {
            'props': {p: getattr(self, p)
                      for p in self._prop_names  # pylint: disable=no-member
                      if hasattr(self, p)},
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
        if isinstance(self.children, collections.MutableSequence):
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
        children = getattr(self, 'children', None)

        # children is just a component
        if isinstance(children, Component):
            yield children
            for t in children.traverse():
                yield t

        # children is a list of components
        elif isinstance(children, collections.MutableSequence):
            for i in children:  # pylint: disable=not-an-iterable
                yield i

                if isinstance(i, Component):
                    for t in i.traverse():
                        yield t

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
        elif isinstance(self.children, collections.MutableSequence):
            for c in self.children:
                length += 1
                if isinstance(c, Component):
                    length += len(c)
        else:
            # string or number
            length = 1
        return length


# pylint: disable=unused-argument
def generate_class(typename, props, description, namespace):
    # Dynamically generate classes to have nicely formatted docstrings,
    # keyword arguments, and repr
    # Insired by http://jameso.be/2013/08/06/namedtuple.html

    # TODO - Tab out the repr for the repr of these components to make it
    # look more like a heirarchical tree
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
    c = '''class {typename}(Component):
        """{docstring}
        """
        def __init__(self, {default_argtext}):
            self._prop_names = {list_of_valid_keys}
            self._type = '{typename}'
            self._namespace = '{namespace}'
            self.available_events = {events}
            self.available_properties = {list_of_valid_keys}

            for k in {required_args}:
                if k not in kwargs:
                    raise Exception(
                        'Required argument `' + k + '` was not specified.'
                    )

            super({typename}, self).__init__({argtext})

        def __repr__(self):
            if(any(getattr(self, c, None) is not None for c in self._prop_names
                   if c is not self._prop_names[0])):

                return (
                    '{typename}(' +
                    ', '.join([c+'='+repr(getattr(self, c, None))
                               for c in self._prop_names
                               if getattr(self, c, None) is not None])+')')

            else:
                return (
                    '{typename}(' +
                    repr(getattr(self, self._prop_names[0], None)) + ')')
    '''

    # pylint: disable=unused-variable
    filtered_props = reorder_props(filter_props(props))
    list_of_valid_keys = repr(list(filtered_props.keys()))
    docstring = create_docstring(
        typename,
        filtered_props,
        parse_events(props),
        description
    )
    events = '[' + ', '.join(parse_events(props)) + ']'
    if 'children' in props:
        default_argtext = 'children=None, **kwargs'
        argtext = 'children=children, **kwargs'
    else:
        default_argtext = '**kwargs'
        argtext = '**kwargs'

    required_args = required_props(props)

    d = c.format(**locals())

    scope = {'Component': Component}
    # pylint: disable=exec-used
    exec(d, scope)
    result = scope[typename]
    return result


def required_props(props):
    return [prop_name for prop_name, prop in list(props.items())
            if prop['required']]


def reorder_props(props):
    # If "children" is a prop, then move it to the front to respect
    # dash convention
    if 'children' in props:
        props = collections.OrderedDict(
            [('children', props.pop('children'), )] +
            list(zip(list(props.keys()), list(props.values())))
        )
    return props


def parse_events(props):
    if ('dashEvents' in props and
            props['dashEvents']['type']['name'] == 'enum'):
        events = [v['value'] for v in props['dashEvents']['type']['value']]
    else:
        events = []
    return events


def create_docstring(name, props, events, description):
    if 'children' in props:
        props = collections.OrderedDict(
            [['children', props.pop('children')]] +
            list(zip(list(props.keys()), list(props.values())))
        )
    return '''A {name} component.{description}

    Keyword arguments:
    {args}

    Available events: {events}'''.format(
        name=name,
        description='\n{}'.format(description),
        args='\n'.join(
            ['- {}'.format(argument_doc(
                p, prop['type'], prop['required'], prop['description']
            )) for p, prop in list(filter_props(props).items())]
        ),
        events=', '.join(events)
    ).replace('    ', '')


def filter_props(args):
    filtered_args = copy.deepcopy(args)
    for arg_name, arg in list(filtered_args.items()):
        if 'type' not in arg:
            filtered_args.pop(arg_name)
            continue

        arg_type = arg['type']['name']
        if arg_type in ['func', 'symbol', 'instanceOf']:
            filtered_args.pop(arg_name)

        # dashEvents are a special oneOf property that is used for subscribing
        # to events but it's never set as a property
        if arg_name in ['dashEvents']:
            filtered_args.pop(arg_name)
    return filtered_args


def js_to_py_type(type_object):
    js_type_name = type_object['name']

    # wrapping everything in lambda to prevent immediate execution
    js_to_py_types = {
        'array': lambda: 'list',
        'bool': lambda: 'boolean',
        'number': lambda: 'number',
        'string': lambda: 'string',
        'object': lambda: 'dict',

        'any': lambda: 'boolean | number | string | dict | list',
        'element': lambda: 'dash component',
        'node': lambda: (
            'a list of or a singular dash component, string or number'
        ),

        # React's PropTypes.oneOf
        'enum': lambda: 'a value equal to: {}'.format(', '.join([
            '{}'.format(str(t['value'])) for t in type_object['value']
        ])),

        # React's PropTypes.oneOfType
        'union': lambda: '{}'.format(' | '.join([
            '{}'.format(js_to_py_type(subType))
            for subType in type_object['value'] if js_to_py_type(subType) != ''
        ])),

        # React's PropTypes.arrayOf
        # pylint: disable=too-many-format-args
        'arrayOf': lambda: 'list'.format(
            'of {}s'.format(js_to_py_type(type_object['value']))
            if js_to_py_type(type_object['value']) != ''
            else ''
        ),

        # React's PropTypes.objectOf
        'objectOf': lambda: (
            'dict with strings as keys and values of type {}'
        ).format(js_to_py_type(type_object['value'])),

        # React's PropTypes.shape
        'shape': lambda: (
            'dict containing keys {}.\n{}'.format(
                ', '.join(
                    ["'{}'".format(t) for t in
                     list(type_object['value'].keys())]
                ),
                'Those keys have the following types: \n{}'.format(
                    '\n'.join([
                        '  - ' + argument_doc(
                            prop_name,
                            prop,
                            prop['required'],
                            prop.get('description', '')
                        ) for
                        prop_name, prop in list(type_object['value'].items())
                    ])
                )
            )
        )
    }

    if 'computed' in type_object and type_object['computed']:
        return ''
    if js_type_name in js_to_py_types:
        return js_to_py_types[js_type_name]()
    return ''


def argument_doc(arg_name, type_object, required, description):
    py_type_name = js_to_py_type(type_object)
    if '\n' in py_type_name:
        return (
            '{name} ({is_required}): {description}. '
            '{name} has the following type: {type}'
        ).format(
            name=arg_name,
            type=py_type_name,
            description=description,
            is_required='required' if required else 'optional'
        )

    return '{name} ({type}{is_required}){description}'.format(
        name=arg_name,
        type='{}; '.format(py_type_name) if py_type_name else '',
        description=(
            ': {}'.format(description) if description != '' else ''
        ),
        is_required='required' if required else 'optional'
    )
