import collections


'''
TODO: Validate this list of supported react elements.

Other valid react attributes include:
https://facebook.github.io/react/docs/tags-and-attributes.html#html-attributes

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
    'high', 'href', 'hrefLang', 'htmlFor', 'httpEquiv', 'icon', 'label',
    'lang', 'list', 'loop', 'low', 'manifest', 'marginHeight',
    'marginWidth', 'max', 'maxLength', 'media', 'mediaGroup',
    'method', 'min', 'multiple', 'muted', 'name', 'noValidate',
    'open', 'optimum', 'pattern', 'placeholder', 'poster', 'preload',
    'radioGroup', 'readOnly', 'rel', 'required', 'role', 'rowSpan',
    'rows', 'sandbox', 'scope', 'scoped', 'scrolling', 'seamless',
    'selected', 'shape', 'size', 'sizes', 'span', 'spellCheck',
    'srcDoc', 'srcSet', 'start', 'step', 'tabIndex', 'target',
    'title', 'type', 'useMap', 'value', 'wmode']
'''


class Component(collections.MutableSequence):
    def __init__(self, **kwargs):
        for required_key in ['content', 'id']:
            if required_key not in kwargs:
                raise Exception("'{}' is a required keyword "
                                "argument.".format(required_key))

        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def to_plotly_json(self):
        return {
            'props': {p: getattr(self, p)
                      for p in self._prop_names if p != 'content'},
            'type': self._type,
            'children': self.content
        }

    def __getitem__(self, id):
        if isinstance(self.content, basestring) or self.content is None:
            raise KeyError

        for item in self.content:
            if isinstance(item, basestring) or self.content is None:
                continue
            elif item.id == id:
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


def generate_class(typename, args):
    # http://jameso.be/2013/08/06/namedtuple.html
    import sys
    c = '''class {typename}(Component):
        """A {typename} component.\nValid keys:\n{bullet_list_of_valid_keys}
        """
        def __init__(self, {default_argtext}):
            self._prop_names = {list_of_valid_keys}
            self._type = '{typename}'
            super({typename}, self).__init__({argtext})

        def __repr__(self):
            if(any(c is not None for c in self._prop_names
                   if c is not "content")):
                return '{typename}('+', '.join([c+'='+repr(getattr(self, c))
                                                for c in self._prop_names])+')'
            else:
                return '{typename}("' + repr(c.content) + '")'
    '''

    list_of_valid_keys = repr(args)
    bullet_list_of_valid_keys = ('- ' + ' (dflt: None)\n- '.join(args) +
                                 ' (dflt: None)')

    default_argtext = ''
    argtext = ''
    for arg in args:
        default_argtext += arg + '=None, '
        argtext += arg + '=' + arg + ', '

    default_argtext = default_argtext[:-2]
    argtext = argtext[:-2]

    d = c.format(**locals())

    namespace = {'Component': Component}
    exec d in namespace
    result = namespace[typename]
    result.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')
    return result

_valid_kwargs = ['content', 'id', 'className', 'style', 'dependencies']

_customelements = [
    {
        'type': 'Dropdown',
        'valid_kwargs': _valid_kwargs + ['options', 'selected']
    },
    {
        'type': 'Slider',
        'valid_kwargs': _valid_kwargs + ['min', 'max', 'step',
                                         'value', 'label']
    },
    {
        'type': 'PlotlyGraph',
        'valid_kwargs': _valid_kwargs + ['figure', 'height']
    }
]

_htmlelements = ['a', 'abbr', 'address', 'area', 'article', 'aside',
                 'audio', 'b', 'base', 'bdi', 'bdo', 'big', 'blockquote',
                 'body', 'br', 'button', 'canvas', 'caption', 'cite', 'code',
                 'col', 'colgroup', 'data', 'datalist', 'dd', 'del', 'details',
                 'dfn', 'dialog', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset',
                 'figcaption', 'figure', 'footer', 'form',
                 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hr',
                 'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'keygen',
                 'label', 'legend', 'li', 'link', 'main', 'map', 'mark',
                 'menu', 'menuitem', 'meta', 'meter', 'nav', 'noscript',
                 'object', 'ol', 'optgroup', 'option', 'output', 'p',
                 'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt',
                 'ruby', 's', 'samp', 'script', 'section', 'select',
                 'small', 'source', 'span', 'strong', 'style', 'sub',
                 'summary', 'sup', 'table', 'tbody', 'td', 'textarea',
                 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'track', 'u',
                 'ul', 'var', 'video', 'wbr']

_invalid_elements = ['del']

for _i in _invalid_elements:
    _htmlelements.remove(_i)

for _h in _htmlelements:
    globals()[_h] = generate_class(_h, _valid_kwargs)

for _s in _customelements:
    globals()[_s['type']] = generate_class(_s['type'], _s['valid_kwargs'])
