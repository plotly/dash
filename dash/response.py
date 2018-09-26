"""
Extended Flask Response for use inside callbacks
"""
import collections
import json
import plotly
from flask import Response
from . import exceptions
from .development.base_component import Component


# pylint: disable=too-many-ancestors
class DashResponse(Response):
    """
    Flask Response extended with option to convert a regular response to
    valid Dash json-encoded component.

    Return a `DashResponse` object from a Dash callback in order to set
    other properties of the response like headers or cookies.
    """
    def __init__(self, output_value, **kwargs):
        super(DashResponse, self).__init__(
            '',  # filled in by set_data later
            mimetype='application/json', **kwargs)
        self.output_value = output_value

    def jsonify_response(self, output):
        """
        Convert the response to valid Dash json-encoded format.

        :param output: Output element for the callback.
        :param validator: Called if json serialization fails with
                          the output value and the `output` element.
        """
        response = {
            'response': {
                'props': {
                    output.component_property: self.output_value
                }
            }
        }

        try:
            json_value = json.dumps(response,
                                    cls=plotly.utils.PlotlyJSONEncoder)
        except TypeError:
            _validate_callback_output(self.output_value, output)
            raise exceptions.InvalidCallbackReturnValue('''
            The callback for property `{property:s}`
            of component `{id:s}` returned a value
            which is not JSON serializable.

            In general, Dash properties can only be
            dash components, strings, dictionaries, numbers, None,
            or lists of those.
            '''.format(property=output.component_property,
                       id=output.component_id))

        self.set_data(json_value)


def _validate_callback_output(output_value, output):
    valid = [str, dict, int, float, type(None), Component]

    def _raise_invalid(bad_val, outer_val, path, index=None, toplevel=False):
        outer_id = "(id={:s})".format(outer_val.id) \
                    if getattr(outer_val, 'id', False) else ''
        outer_type = type(outer_val).__name__
        bad_type = type(bad_val).__name__
        raise exceptions.InvalidCallbackReturnValue('''
        The callback for property `{property:s}` of component `{id:s}`
        returned a {object:s} having type `{type:s}`
        which is not JSON serializable.

        {location_header:s}{location:s}
        and has string representation
        `{bad_val}`

        In general, Dash properties can only be
        dash components, strings, dictionaries, numbers, None,
        or lists of those.
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
                        bad_val=j,
                        outer_val=val,
                        path=p,
                        index=index
                    )

                # Children that are not of type Component or
                # list/tuple not returned by traverse
                child = getattr(j, 'children', None)
                if not isinstance(child, (tuple,
                                          collections.MutableSequence)):
                    if child and not _value_is_valid(child):
                        _raise_invalid(
                            bad_val=child,
                            outer_val=val,
                            path=p + "\n" + "[*] " + type(child).__name__,
                            index=index
                        )

            # Also check the child of val, as it will not be returned
            child = getattr(val, 'children', None)
            if not isinstance(child, (tuple, collections.MutableSequence)):
                if child and not _value_is_valid(child):
                    _raise_invalid(
                        bad_val=child,
                        outer_val=val,
                        path=type(child).__name__,
                        index=index
                    )

        # val is not a Component, but is at the top level of tree
        else:
            if not _value_is_valid(val):
                _raise_invalid(
                    bad_val=val,
                    outer_val=type(val).__name__,
                    path='',
                    index=index,
                    toplevel=True
                )

    if isinstance(output_value, list):
        for i, val in enumerate(output_value):
            _validate_value(val, index=i)
    else:
        _validate_value(output_value)
