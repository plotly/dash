import functools
import hashlib
import base64
import pkgutil


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


def get_asset_path(
        requests_pathname,
        routes_pathname,
        asset_path,
        asset_url_path):

    i = requests_pathname.rfind(routes_pathname)
    req = requests_pathname[:i]

    return '/'.join([
        # Only take the first part of the pathname
        req,
        asset_url_path,
        asset_path
    ])


def pluck(obj, *props, **additions):
    return dict({k: v for k, v in obj.items() if k in props}, **additions)


def first_key(data, *keys):
    for key in keys:
        value = data.get(key)
        if value:
            return key, value
    return None, None


@functools.lru_cache()
def integrity_hash_from_file(filename):
    with open(filename, 'rb') as f:
        h = hashlib.sha384(f.read())

    return 'sha384-{}'.format(
        base64.b64encode(h.digest()).decode()
    )


@functools.lru_cache()
def integrity_hash_from_package(namespace, path):
    h = hashlib.sha384(pkgutil.get_data(namespace, path))

    return 'sha384-{}'.format(
        base64.b64encode(h.digest()).decode()
    )


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
