import collections
from . import exceptions
from .development.base_component import Component


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


def _raise_invalid(output, bad_val, outer_val, bad_type, path, index=None,
                   toplevel=False):
    outer_id = "(id={:s})".format(outer_val.id) \
                if getattr(outer_val, 'id', False) else ''
    outer_type = type(outer_val).__name__
    raise exceptions.InvalidCallbackReturnValue('''
    The callback for property `{property:s}` of component `{id:s}`
    returned a {object:s} having type `{type:s}`
    which can not be serialized by Dash.

    {location_header:s}{location:s}
    and has string representation
    `{bad_val}`

    In general, Dash properties can only be
    dash components, strings, dictionaries, numbers, None,
    or un-nested lists of those.
    '''.format(
        property=output.component_property,
        id=output.component_id,
        object='tree with one value' if not toplevel else 'value',
        type=bad_type,
        location_header=(
            'The value in question is located at'
            if not toplevel else
            '''The value in question is either the only value returned,
            or is in the top level of the returned list,'''
        ),
        location=(
            "\n" +
            ("[{:d}] {:s} {:s}".format(index, outer_type, outer_id)
             if index is not None
             else ('[*] ' + outer_type + ' ' + outer_id))
            + "\n" + path + "\n"
        ) if not toplevel else '',
        bad_val=bad_val).replace('    ', ''))


def _validate_callback_output(output_value, output):
    valid = [str, dict, int, float, type(None), Component]

    def _value_is_valid(val):
        return (
            # pylint: disable=unused-variable
            any([isinstance(val, x) for x in valid]) or
            type(val).__name__ == 'unicode'
        )

    def _validate_value(val, index=None):
        # val is a Component
        if isinstance(val, Component):
            for p, j in val.traverse_with_paths():
                # check each component value in the tree
                if not _value_is_valid(j):
                    _raise_invalid(
                        output=output,
                        bad_val=j,
                        outer_val=val,
                        bad_type=type(j).__name__,
                        path=p,
                        index=index
                    )

                # Children that are not of type Component or
                # collections.MutableSequence not returned by traverse
                child = getattr(j, 'children', None)
                if not isinstance(child, collections.MutableSequence):
                    if child and not _value_is_valid(child):
                        _raise_invalid(
                            output=output,
                            bad_val=child,
                            outer_val=val,
                            bad_type=type(child).__name__,
                            path=p + "\n" + "[*] " + type(child).__name__,
                            index=index
                        )

            # Also check the child of val, as it will not be returned
            child = getattr(val, 'children', None)
            if not isinstance(child, collections.MutableSequence):
                if child and not _value_is_valid(child):
                    _raise_invalid(
                        output=output,
                        bad_val=child,
                        outer_val=val,
                        bad_type=type(child).__name__,
                        path=type(child).__name__,
                        index=index
                    )

        # val is not a Component, but is at the top level of tree
        else:
            if not _value_is_valid(val):
                _raise_invalid(
                    output=output,
                    bad_val=val,
                    outer_val=type(val).__name__,
                    bad_type=type(val).__name__,
                    path='',
                    index=index,
                    toplevel=True
                )

    if isinstance(output_value, list):
        for i, val in enumerate(output_value):
            _validate_value(val, index=i)
    else:
        _validate_value(output_value)


def _validate_children_callback_output(output_value, output):

    def _is_nested_list(value):
        if isinstance(value, list):
            for subval in value:
                if isinstance(subval, list):
                    return True
        return False

    def _validate_value(val, index=None):
        # Make sure there are no nested dicts in component tree
        if isinstance(val, Component):
            for p, j in val.traverse_with_paths():
                child = getattr(j, 'children', None)
                if _is_nested_list(child):
                    _raise_invalid(
                        output=output,
                        bad_val=child,
                        outer_val=j,
                        bad_type=type(child).__name__,
                        path=p,
                        index=index
                    )
            child = getattr(val, 'children', None)
            if _is_nested_list(child):
                _raise_invalid(
                    output=output,
                    bad_val=child,
                    outer_val=val,
                    bad_type=type(child).__name__,
                    path='',
                    index=index
                )
    if isinstance(output_value, list):
        for i, val in enumerate(output_value):
            if isinstance(val, list):
                _raise_invalid(
                    output=output,
                    bad_val=val,
                    outer_val=output_value,
                    bad_type=type(val).__name__,
                    path='',
                )
            _validate_value(val, index=i)
    else:
        _validate_value(output_value)
