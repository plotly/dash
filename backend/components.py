
# TODO: deal with non-closing HTML tags
# TODO: deal with the rest of the available html attributes like href etc
# TODO: better hidden/private module variables
_htmlelements = ['a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b', 'base', 'bdi', 'bdo', 'big', 'blockquote', 'body', 'br','button', 'canvas', 'caption', 'cite', 'code', 'col', 'colgroup', 'data', 'datalist', 'dd', 'del', 'details', 'dfn','dialog', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5','h6', 'head', 'header', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'keygen', 'label', 'legend', 'li', 'link','main', 'map', 'mark', 'menu', 'menuitem', 'meta', 'meter', 'nav', 'noscript', 'object', 'ol', 'optgroup', 'option','output', 'p', 'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section', 'select','small', 'source', 'span', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th','thead', 'time', 'title', 'tr', 'track', 'u', 'ul', 'var', 'video', 'wbr']
_valid_kwargs = ['className', 'id', 'style', 'dependencies']

# TODO: dang, brutal to just repeat these propTypes.
# TODO: lowercase, uppercase?
_statefulelements = [
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


def _componentfactory(name, valid_kwargs, default_kwargs):
    def __init__(self, props={}, children=''):
        self._props = props
        self._children = children
        for key, value in props.items():
            if key not in valid_kwargs:
                raise TypeError("{} is not valid for {}".format(
                    key,
                    self.__class__.__name__))

        dict.__init__(self, props=props, children=children, **default_kwargs)

    def __repr__(self):
        return '{}({}, {})'.format(
            self.__class__.__name__,
            repr(self._props),
            repr(self._children))

    def __str__(self):
        return str(dict(**self))

    newcomponentclass = type(name, (dict,), {
        "__init__": __init__,
        "__repr__": __repr__,
        "__str__": __str__
    })

    return newcomponentclass


for _h in _htmlelements:
    _generated_class = _componentfactory(_h, _valid_kwargs, {'type': _h})
    globals()[_generated_class.__name__] = _generated_class

for _s in _statefulelements:
    _generated_class = _componentfactory(
        _s['type'], _s['valid_kwargs'], {'type': _s['type']})
    globals()[_generated_class.__name__] = _generated_class
