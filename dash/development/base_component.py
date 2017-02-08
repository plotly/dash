import collections
import types


class Component(collections.MutableMapping):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k not in self._prop_names:
                # TODO - What's the right exception here?
                raise Exception(
                    'Unexpected keyword argument `{}`'.format(k) +
                    '\nAllowed arguments: {}'.format(
                        ', '.join(self._prop_names)
                    )
                )
            setattr(self, k, v)

    def to_plotly_json(self):
        as_json = {
            'props': {p: getattr(self, p)
                      for p in self._prop_names
                      if hasattr(self, p)},
            'type': self._type,
            'namespace': self._namespace
        }
        if hasattr(self, 'dependencies'):
            as_json['dependencies'] = self.dependencies
        return as_json

    def _check_if_has_indexable_content(self, item):
        if (not hasattr(item, 'content') or
                item.content is None or
                isinstance(item.content, basestring)):
            raise KeyError

    def _get_set_or_delete(self, id, operation, new_item=None):
        self._check_if_has_indexable_content(self)

        if isinstance(self.content, Component):
            if getattr(self.content, 'id', None) is not None:
                if self.content.id == id:
                    if operation == 'get':
                        return self.content
                    elif operation == 'set':
                        self.content = new_item
                        return
                    elif operation == 'delete':
                        self.content = None
                        return
                else:
                    raise KeyError

        # if content is like a list
        for (i, item) in enumerate(self.content):
            # If the item itself is the one we're looking for
            if getattr(item, 'id', None) == id:
                if operation == 'get':
                    return item
                elif operation == 'set':
                    self.content[i] = new_item
                    return
                elif operation == 'delete':
                    del self.content[i]
                    return

            # Otherwise, recursively dig into that items subtree
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

        raise KeyError

    # Supply ABC methods for a MutableMapping:
    # - __getitem__
    # - __setitem__
    # - __delitem__
    # - __iter__
    # - __len__

    def __getitem__(self, id):
        '''Recursively find the element with the given ID through the tree
        of content.
        '''
        # TODO - Rename content to children
        # A component's content can be undefined, a string, another component,
        # or a list of components.
        return self._get_set_or_delete(id, 'get')

    def __setitem__(self, id, item):
        return self._get_set_or_delete(id, 'set', item)

    def __delitem__(self, id):
        return self._get_set_or_delete(id, 'delete')

    def __iter__(self):
        content = getattr(self, 'content', None)

        # content is just a component
        if (isinstance(content, Component) and
                getattr(self.content, 'id', None) is not None):

            yield self.content.id

        # content is a list of components
        # TODO - Stronger check for list?
        if (not isinstance(content, basestring) and
                not isinstance(content, Component) and
                content is not None):

            for i in content:

                if getattr(i, 'id', None) is not None:
                    yield i.id

                if hasattr(i, 'content'):
                    for t in i.__iter__():
                        yield t

    def __len__(self):
        '''Return the number of items in the tree
        '''
        l = 0
        if getattr(self, 'content', None) is None:
            l = 0
        elif isinstance(self.content, basestring):
            l = 1
        elif isinstance(self.content, Component):
            l = 1
        else:
            for c in self.content:
                l += 1
                l += len(c)
        return l


def generate_class(typename, component_arguments, namespace):
    # Dynamically generate classes to have nicely formatted docstrings,
    # keyword arguments, and repr
    # Insired by http://jameso.be/2013/08/06/namedtuple.html

    import sys

    # TODO - Tab out the repr for the repr of these components to make it
    # look more like a heirarchical tree
    # TODO - Include "description" "defaultValue" in the repr and docstring
    # TODO - Handle "required"
    # TODO - How to handle user-given `null` values? I want to include
    # an expanded docstring like Dropdown(value=None, id=None)
    # but by templating in those None values, I have no way of knowing
    # whether a property is None because the user explicitly wanted
    # it to be `null` or whether that was just the default value.
    # The solution might be to deal with default values better although
    # not all component authors will supply those.
    c = '''class {typename}(Component):
        """A {typename} component.\nValid keys:\n{bullet_list_of_valid_keys}
        """
        def __init__(self, {default_argtext}):
            self._prop_names = {list_of_valid_keys}
            self._type = '{typename}'
            self._namespace = '{namespace}'
            super({typename}, self).__init__({argtext})

        def __repr__(self):
            if(any(getattr(self, c, None) is not None for c in self._prop_names
                   if c is not self._prop_names[0])):

                return '{typename}('+', '.join([c+'='+repr(getattr(self, c, None))
                                                for c in self._prop_names if getattr(self, c, None) is not None])+')'

            else:
                return '{typename}(' + repr(getattr(self, self._prop_names[0], None)) + ')'
    '''
    list_of_valid_keys = repr(component_arguments)
    bullet_list_of_valid_keys = ('- ' + '\n- '.join(
        component_arguments
    ))

    if 'content' in component_arguments:
        default_argtext = 'content=None, **kwargs'
        argtext = 'content=content, **kwargs'
    else:
        default_argtext = '**kwargs'
        argtext = '**kwargs'

    d = c.format(**locals())

    scope = {'Component': Component}
    exec d in scope
    result = scope[typename]
    return result
