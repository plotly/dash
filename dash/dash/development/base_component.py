import collections

class Component(collections.MutableSequence):
    def __init__(self, **kwargs):
        if 'dependencies' in kwargs:
            self.dependencies = kwargs['dependencies']

        self.content = kwargs.get('content', None)

    def to_plotly_json(self):
        as_json = {
            'props': {p: getattr(self, p)
                      for p in self._prop_names
                      if p != 'content' and hasattr(self, p)},
            'type': self._type,
            'children': self.content
        }
        if hasattr(self, 'dependencies'):
            as_json['dependencies'] = self.dependencies
        return as_json

    def __getitem__(self, id):
        if isinstance(self.content, basestring) or self.content is None:
            raise KeyError

        for item in self.content:
            if isinstance(item, basestring) or self.content is None:
                continue
            elif getattr(item, 'id', None) == id:
                return item
            try:
                component = item[id]
            except:
                pass
            else:
                return component
        raise KeyError

    def __setitem__(self, index, component):
        if isinstance(self.content, basestring) or self.content is None:
            raise KeyError
        self.content.__setitem__(index, component)

    def __delitem__(self, id):
        if isinstance(self.content, basestring) or self.content is None:
            raise KeyError

        for i, item in enumerate(self.content):
            if isinstance(item, basestring) or self.content is None:
                continue
            else:
                if item.id == id:
                    self.content.__delitem__(i)
                    return
            try:
                item.__delitem__(id)
            except:
                pass
            else:
                return
        raise KeyError

    def __len__(self):
        if isinstance(self.content, basestring) or self.content is None:
            return 1
        else:
            count = 1
            for item in self.content:
                if (isinstance(self.content, basestring) or
                   self.content is None):
                    count += 1
                else:
                    count += item.__len__()
            return count

    def insert(self, index, component):
        if isinstance(self.content, basestring) or self.content is None:
            self.content = [self.content]
        self.content.insert(index, component)


def generate_class(typename, component_arguments, setup):
    # http://jameso.be/2013/08/06/namedtuple.html
    import sys
    c = '''class {typename}(Component):
        """A {typename} component.\nValid keys:\n{bullet_list_of_valid_keys}
        """
        def __init__(self, {default_argtext}):
            self._prop_names = {list_of_valid_keys}
            self._type = '{typename}'
            super({typename}, self).__init__({argtext})
            setup(self)

        def __repr__(self):
            if(any(getattr(self, c, None) is not None for c in self._prop_names
                   if c is not "content")):
                return '{typename}(\\n    '+', \\n    '.join([c+'='+repr(getattr(self, c, None))
                                                for c in self._prop_names if getattr(self, c, None) is not None])+'\\n)'
            else:
                return '{typename}(' + repr(self.content) + ')'
    '''
    # every component will at least have `content` and `className` arguments
    keyword_arguments = ['content', 'className']
    keyword_arguments.extend([s for s in component_arguments if s not in keyword_arguments])
    list_of_valid_keys = repr(keyword_arguments)
    bullet_list_of_valid_keys = ('- ' + ' (dflt: None)\n- '.join(keyword_arguments) +
                                 ' (dflt: None)')

    default_argtext = ''
    argtext = ''
    for arg in keyword_arguments:
        default_argtext += arg + '=None, '
        argtext += arg + '=' + arg + ', '

    default_argtext += '**kwargs'
    argtext = argtext[:-2]

    d = c.format(**locals())

    namespace = {'Component': Component, 'setup': setup}
    exec d in namespace
    result = namespace[typename]
    # result.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')
    return result
