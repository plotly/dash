"""
Extended Flask Response for using inside a callbacks
"""
import json
import plotly
from flask import Response


class DashResponse(Response):
    """
    Flask Response extended with option to convert a regular response to
    valid Dash json-encoded
    """
    def __init__(self, *args, **kwargs):
        self.dash_response = args[0] if args else None
        super(DashResponse, self).__init__(
            mimetype='application/json', *args, **kwargs)

    def jsonify_response(self, output):
        """
        convert response to valid Dash json-encoded
        :param output: output element for the callback
        :return:
        """
        response = {
            'response': {
                'props': {
                    output.component_property: self.dash_response
                }
            }
        }
        self.set_data(
            json.dumps(response, cls=plotly.utils.PlotlyJSONEncoder)
        )
