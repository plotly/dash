import flask
import datetime
import plotly
import requests


def login():
    authorization_header = flask.request.headers.get('Authorization')
    oauth_token = authorization_header.split('Bearer ')[1]
    res = requests.get(
        '{}/v2/users/current'.format(
            plotly.config.get_config()['plotly_api_domain']
        ),
        headers={
            'Authorization': authorization_header
        }
    )
    res.raise_for_status()
    response = flask.Response(
        res.json(),
        status=res.status_code
    )
    # TODO - set path appropriately
    response.set_cookie(
        'plotly_dash_oauth_token',
        value=oauth_token,
        max_age=None
    )
    return response

