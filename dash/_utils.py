import collections


def convert_unicode_to_string(data):
    """Recursively converts dictionary keys to strings.
    This ensures python2.7 does not load a dict with unicode keys."""
    if type(data).__name__ == 'unicode':
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_unicode_to_string, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_unicode_to_string, data))
    return data


def interpolate_str(template, **data):
    s = template
    for k, v in data.items():
        key = '{%' + k + '%}'
        s = s.replace(key, v)
    return s


def format_tag(tag_name, attributes, inner='', closed=False, opened=False):
    tag = '<{tag} {attributes}'
    if closed:
        tag += '/>'
    elif opened:
        tag += '>'
    else:
        tag += '>' + inner + '</{tag}>'
    return tag.format(
        tag=tag_name,
        attributes=' '.join([
            '{}="{}"'.format(k, v) for k, v in attributes.items()]))


class AttributeDict(dict):
    """
    Dictionary subclass enabling attribute lookup/assignment of keys/values.

    For example::
        >>> m = AttributeDict({'foo': 'bar'})
        >>> m.foo
        'bar'
        >>> m.foo = 'not bar'
        >>> m['foo']
        'not bar'
    ``AttributeDict`` objects also provide ``.first()`` which acts like
    ``.get()`` but accepts multiple keys as arguments, and returns the value of
    the first hit, e.g.::
        >>> m = AttributeDict({'foo': 'bar', 'biz': 'baz'})
        >>> m.first('wrong', 'incorrect', 'foo', 'biz')
        'bar'
    """

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # to conform with __getattr__ spec
            raise AttributeError(key)

    # pylint: disable=inconsistent-return-statements
    def first(self, *names):
        for name in names:
            value = self.get(name)
            if value:
                return value
