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
    """
    Dynamically generate classes to have nicely formatted docstrings,
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
    c = '''class {typename}(Component):
    """{docstring}"""
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

        for k in {required_args}:
            if k not in kwargs:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

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
    list_of_valid_keys = repr(list(filtered_props.keys()))
    # pylint: disable=unused-variable
    docstring = create_docstring(
        component_name=typename,
        props=filtered_props,
        events=parse_events(props),
        description=description)

    # pylint: disable=unused-variable
    events = '[' + ', '.join(parse_events(props)) + ']'
    if 'children' in props:
        default_argtext = 'children=None, **kwargs'
        # pylint: disable=unused-variable
        argtext = 'children=children, **kwargs'
    else:
        default_argtext = '**kwargs'
        argtext = '**kwargs'

    required_args = required_props(props)

    scope = {'Component': Component}
    # pylint: disable=exec-used
    exec(c.format(**locals()), scope)
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
        events = []

    return events


def parse_wildcards(props):
    """
    Pull out the wildcard attributes from the Component props

    Parameters
    ----------
    props: dict
        Dictionary with {propName: propMetadata} structure

    Returns
    -------
    list
        List of Dash valid wildcard prefixes
    """
    list_of_valid_wildcard_attr_prefixes = []
    for wildcard_attr in ["data-*", "aria-*"]:
        if wildcard_attr in props.keys():
            list_of_valid_wildcard_attr_prefixes.append(wildcard_attr[:-1])
    return list_of_valid_wildcard_attr_prefixes


def reorder_props(props):
    """
    If "children" is in props, then move it to the
    front to respect dash convention

    Parameters
    ----------
    props: dict
        Dictionary with {propName: propMetadata} structure

    Returns
    -------
    dict
        Dictionary with {propName: propMetadata} structure
    """
    if 'children' in props:
        props = collections.OrderedDict(
            [('children', props.pop('children'),)] +
            list(zip(list(props.keys()), list(props.values()))))

    return props


def filter_props(props):
    """
    Filter props from the Component arguments to exclude:
        - Those without a "type" or a "flowType" field
        - Those with arg.type.name in {'func', 'symbol', 'instanceOf'}
        - dashEvents as a name

    Parameters
    ----------
    props: dict
        Dictionary with {propName: propMetadata} structure

    Returns
    -------
    dict
        Filtered dictionary with {propName: propMetadata} structure

    Examples
    --------
    ```python
    prop_args = {
        'prop1': {
            'type': {'name': 'bool'},
            'required': False,
            'description': 'A description',
            'flowType': {},
            'defaultValue': {'value': 'false', 'computed': False},
        },
        'prop2': {'description': 'A prop without a type'},
        'prop3': {
            'type': {'name': 'func'},
            'description': 'A function prop',
        },
    }
    # filtered_prop_args is now
    # {
    #    'prop1': {
    #        'type': {'name': 'bool'},
    #        'required': False,
    #        'description': 'A description',
    #        'flowType': {},
    #        'defaultValue': {'value': 'false', 'computed': False},
    #    },
    # }
    filtered_prop_args = filter_props(prop_args)
    ```
    """
    filtered_props = copy.deepcopy(props)

    for arg_name, arg in list(filtered_props.items()):
        if 'type' not in arg and 'flowType' not in arg:
            filtered_props.pop(arg_name)
            continue

        # Filter out functions and instances --
        # these cannot be passed from Python
        if 'type' in arg:  # These come from PropTypes
            arg_type = arg['type']['name']
            if arg_type in {'func', 'symbol', 'instanceOf'}:
                filtered_props.pop(arg_name)
        elif 'flowType' in arg:  # These come from Flow & handled differently
            arg_type_name = arg['flowType']['name']
            if arg_type_name == 'signature':
                # This does the same as the PropTypes filter above, but "func"
                # is under "type" if "name" is "signature" vs just in "name"
                if 'type' not in arg['flowType'] \
                        or arg['flowType']['type'] != 'object':
                    filtered_props.pop(arg_name)
        else:
            raise ValueError

        # dashEvents are a special oneOf property that is used for subscribing
        # to events but it's never set as a property
        if arg_name in ['dashEvents']:
            filtered_props.pop(arg_name)
    return filtered_props


# pylint: disable=too-many-arguments
def create_prop_docstring(prop_name, type_object, required, description,
                          indent_num, is_flow_type=False):
    """
    Create the Dash component prop docstring

    Parameters
    ----------
    prop_name: str
        Name of the Dash component prop
    type_object: dict
        react-docgen-generated prop type dictionary
    required: bool
        Component is required?
    description: str
        Dash component description
    indent_num: int
        Number of indents to use for the context block
        (creates 2 spaces for every indent)
    is_flow_type: bool
        Does the prop use Flow types? Otherwise, uses PropTypes

    Returns
    -------
    str
        Dash component prop docstring
    """
    py_type_name = js_to_py_type(
        type_object=type_object,
        is_flow_type=is_flow_type,
        indent_num=indent_num + 1)

    indent_spacing = '  ' * indent_num
    if '\n' in py_type_name:
        return '{indent_spacing}- {name} ({is_required}): {description}. ' \
               '{name} has the following type: {type}'.format(
                   indent_spacing=indent_spacing,
                   name=prop_name,
                   type=py_type_name,
                   description=description,
                   is_required='required' if required else 'optional')
    return '{indent_spacing}- {name} ({type}' \
           '{is_required}){description}'.format(
               indent_spacing=indent_spacing,
               name=prop_name,
               type='{}; '.format(py_type_name) if py_type_name else '',
               description=(
                   ': {}'.format(description) if description != '' else ''
               ),
               is_required='required' if required else 'optional')


def map_js_to_py_types_prop_types(type_object):
    """Mapping from the PropTypes js type object to the Python type"""
    return dict(
        array=lambda: 'list',
        bool=lambda: 'boolean',
        number=lambda: 'number',
        string=lambda: 'string',
        object=lambda: 'dict',
        any=lambda: 'boolean | number | string | dict | list',
        element=lambda: 'dash component',
        node=lambda: 'a list of or a singular dash '
                     'component, string or number',

        # React's PropTypes.oneOf
        enum=lambda: 'a value equal to: {}'.format(
            ', '.join(
                '{}'.format(str(t['value']))
                for t in type_object['value'])),

        # React's PropTypes.oneOfType
        union=lambda: '{}'.format(
            ' | '.join(
                '{}'.format(js_to_py_type(subType))
                for subType in type_object['value']
                if js_to_py_type(subType) != '')),

        # React's PropTypes.arrayOf
        arrayOf=lambda: 'list'.format(  # pylint: disable=too-many-format-args
            ' of {}s'.format(
                js_to_py_type(type_object['value']))
            if js_to_py_type(type_object['value']) != ''
            else ''),

        # React's PropTypes.objectOf
        objectOf=lambda: (
            'dict with strings as keys and values of type {}'
            ).format(
                js_to_py_type(type_object['value'])),

        # React's PropTypes.shape
        shape=lambda: 'dict containing keys {}.\n{}'.format(
            ', '.join(
                "'{}'".format(t)
                for t in list(type_object['value'].keys())),
            'Those keys have the following types: \n{}'.format(
                '\n'.join(create_prop_docstring(
                    prop_name=prop_name,
                    type_object=prop,
                    required=prop['required'],
                    description=prop.get('description', ''),
                    indent_num=1)
                          for prop_name, prop in
                          list(type_object['value'].items())))),
    )


def map_js_to_py_types_flow_types(type_object):
    """Mapping from the Flow js types to the Python type"""
    return dict(
        array=lambda: 'list',
        boolean=lambda: 'boolean',
        number=lambda: 'number',
        string=lambda: 'string',
        Object=lambda: 'dict',
        any=lambda: 'bool | number | str | dict | list',
        Element=lambda: 'dash component',
        Node=lambda: 'a list of or a singular dash '
                     'component, string or number',

        # React's PropTypes.oneOfType
        union=lambda: '{}'.format(
            ' | '.join(
                '{}'.format(js_to_py_type(subType))
                for subType in type_object['elements']
                if js_to_py_type(subType) != '')),

        # Flow's Array type
        Array=lambda: 'list{}'.format(
            ' of {}s'.format(
                js_to_py_type(type_object['elements'][0]))
            if js_to_py_type(type_object['elements'][0]) != ''
            else ''),

        # React's PropTypes.shape
        signature=lambda indent_num: 'dict containing keys {}.\n{}'.format(
            ', '.join("'{}'".format(d['key'])
                      for d in type_object['signature']['properties']),
            '{}Those keys have the following types: \n{}'.format(
                '  ' * indent_num,
                '\n'.join(
                    create_prop_docstring(
                        prop_name=prop['key'],
                        type_object=prop['value'],
                        required=prop['value']['required'],
                        description=prop['value'].get('description', ''),
                        indent_num=indent_num,
                        is_flow_type=True)
                    for prop in type_object['signature']['properties']))),
    )


def js_to_py_type(type_object, is_flow_type=False, indent_num=0):
    """
    Convert JS types to Python types for the component definition

    Parameters
    ----------
    type_object: dict
        react-docgen-generated prop type dictionary
    is_flow_type: bool
        Does the prop use Flow types? Otherwise, uses PropTypes
    indent_num: int
        Number of indents to use for the docstring for the prop

    Returns
    -------
    str
        Python type string
    """
    js_type_name = type_object['name']
    js_to_py_types = map_js_to_py_types_flow_types(type_object=type_object) \
        if is_flow_type \
        else map_js_to_py_types_prop_types(type_object=type_object)

    if 'computed' in type_object and type_object['computed'] \
            or type_object.get('type', '') == 'function':
        return ''
    elif js_type_name in js_to_py_types:
        if js_type_name == 'signature':  # This is a Flow object w/ signature
            return js_to_py_types[js_type_name](indent_num)
        # All other types
        return js_to_py_types[js_type_name]()
    return ''
