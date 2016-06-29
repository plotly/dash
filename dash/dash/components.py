import collections
from component_loader import load_components

component_suites_paths = [
    '../renderer/node_modules/dash-core-components/lib/metadata.json',
    '../renderer/node_modules/dash-html-components/lib/metadata.json'
];

# Other valid react attributes include:
# https://facebook.github.io/react/docs/tags-and-attributes.html#html-attributes

# TODO: Resolve conflict with attributes defined in `dash-html-components`
supported_react_attributes = [
    'src', 'height', 'width', 'accept',
    'acceptCharset', 'accessKey', 'action', 'allowFullScreen',
    'allowTransparency', 'alt', 'async', 'autoComplete', 'autoFocus',
    'autoPlay', 'cellPadding', 'cellSpacing', 'charSet', 'checked',
    'classID', 'colSpan', 'cols', 'content', 'contentEditable',
    'contextMenu', 'controls', 'coords', 'crossOrigin', 'data',
    'dateTime', 'defer', 'dir', 'disabled', 'download', 'draggable',
    'encType', 'form', 'formAction', 'formEncType', 'formMethod',
    'formNoValidate', 'formTarget', 'frameBorder', 'headers', 'hidden',
    'high', 'href', 'hrefLang', 'htmlFor', 'httpEquiv', 'icon',
    'lang', 'list', 'loop', 'low', 'manifest', 'marginHeight',
    'marginWidth', 'max', 'maxLength', 'media', 'mediaGroup',
    'method', 'min', 'multiple', 'muted', 'name', 'noValidate',
    'open', 'optimum', 'pattern', 'placeholder', 'poster', 'preload',
    'radioGroup', 'readOnly', 'rel', 'required', 'role', 'rowSpan',
    'rows', 'sandbox', 'scope', 'scoped', 'scrolling', 'seamless',
    'selected', 'shape', 'size', 'sizes', 'span', 'spellCheck',
    'srcDoc', 'srcSet', 'start', 'step', 'tabIndex', 'target',
    'title', 'type', 'useMap', 'value', 'wmode']
# TODO: add `label` back - it conflicts with the actual html element type I think


class Component(collections.MutableSequence):
    def __init__(self, **kwargs):
        for required_key in ['content', 'id']:
            if required_key not in kwargs:
                raise Exception("'{}' is a required keyword "
                                "argument.".format(required_key))

        for k, v in kwargs.iteritems():
            if k in ['id', 'content', 'className', 'style', 'selected'] or v is not None:  # not sure about this -- sometimes the user will want to send up None, like to clear the output cell
                setattr(self, k, v)
        if 'dependencies' in kwargs:
            self.dependencies = kwargs['dependencies']

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


def generate_class(typename, args, setup):
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
    args.extend([s for s in supported_react_attributes if s not in args])
    list_of_valid_keys = repr(args)
    bullet_list_of_valid_keys = ('- ' + ' (dflt: None)\n- '.join(args) +
                                 ' (dflt: None)')

    default_argtext = ''
    argtext = ''
    for arg in args:
        default_argtext += arg + '=None, '
        argtext += arg + '=' + arg + ', '

    default_argtext += '**kwargs'
    argtext = argtext[:-2]

    d = c.format(**locals())

    namespace = {'Component': Component, 'setup': setup}
    exec d in namespace
    result = namespace[typename]
    result.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')
    return result


def empty(self):
    pass


def init_dropdown(self):
    if self.selected is None:
        self.selected = self.options[0]['val']


_valid_kwargs = ['content', 'id', 'className', 'style', 'dependencies']

# Load in external component suites and generate classes for them
_component_suites = [load_components(path, _valid_kwargs) for path in component_suites_paths]

for suite in _component_suites:
    for _c in suite:
        globals()[_c['type']] = generate_class(_c['type'],
                                           _c['valid_kwargs'],
                                           _c['setup'])


def gen_table(rows, header=[]):
    tbl = table([
        thead([
            tr([
                th(h) for h in header
            ])
        ]),
        tbody([
            tr([
                td(cell) for cell in row
            ]) for row in rows
        ])
    ])
    return tbl
