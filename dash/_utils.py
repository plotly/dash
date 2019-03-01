import uuid
import collections
import six


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


def generate_hash():
    return str(uuid.uuid4().hex).strip('-')


def get_asset_path(
        requests_pathname,
        asset_path,
        asset_url_path):

    return '/'.join([
        # Only take the first part of the pathname
        requests_pathname.rstrip('/'),
        asset_url_path,
        asset_path
    ])


# pylint: disable=no-member
def patch_collections_abc(member):
    if six.PY2:
        return getattr(collections, member)
    return getattr(collections.abc, member)


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


def create_callback_id(output):
    if isinstance(output, (list, tuple)):
        return '..{}..'.format('...'.join(
            '{}.{}'.format(x.component_id, x.component_property)
            for x in output
        ))

    return '{}.{}'.format(
        output.component_id, output.component_property
    )
