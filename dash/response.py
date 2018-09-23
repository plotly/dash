"""
Extended Flask Response for use inside callbacks
"""
import json
import plotly
from flask import Response
from . import exceptions


# pylint: disable=too-many-ancestors
class DashResponse(Response):
    """
    Flask Response extended with option to convert a regular response to
    valid Dash json-encoded component.

    Return a `DashResponse` object from a Dash callback in order to set
    other properties of the response like headers or cookies.
    """
    def __init__(self, response, **kwargs):
        self.dash_response = response
        super(DashResponse, self).__init__(
            '',  # filled in by set_data later
            mimetype='application/json', **kwargs)

    def jsonify_response(self, output, validator):
        """
        convert response to valid Dash json-encoded
        :param output: output element for the callback
        :param validator: called if json serialization fails with
                          the output value and the `output` element
        :return: this object
        """
        response = {
            'response': {
                'props': {
                    output.component_property: self.dash_response
                }
            }
        }

        try:
            json_value = json.dumps(response,
                                    cls=plotly.utils.PlotlyJSONEncoder)
        except TypeError:
            validator(self.dash_response, output)
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
        return self
