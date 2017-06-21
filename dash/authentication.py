import flask
import datetime
import json
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
        json.dumps(res.json()),
        mimetype='application/json',
        status=res.status_code
    )
    # TODO - set path appropriately
    response.set_cookie(
        'plotly_oauth_token',
        value=oauth_token,
        max_age=None
    )
    return response


def check_view_access(oauth_token, fid):
    res = requests.get(
        '{}/v2/files/{}'.format(
            plotly.config.get_config()['plotly_api_domain'],
            fid
        ),
        headers={
            'Authorization': 'Bearer {}'.format(oauth_token)
        }
    )
    if res.status_code == 200:
        return True
    elif res.status_code == 404:
        return False
    else:
        # TODO - Dash exception
        raise Exception('Failed request to plotly')


def create_requires_auth(f,
                         fid,
                         access_codes,
                         create_access_codes,
                         auth_cookie_name,
                         *args,
                         **kwargs):
    if fid is None:
        return f(*args, **kwargs)
    else:
        if 'plotly_oauth_token' not in flask.request.cookies:
            return flask.Response(status=403)
        oauth_token = flask.request.cookies['plotly_oauth_token']

        if (datetime.datetime.now() > access_codes['expiration']):
            access_codes = create_access_codes()

        if auth_cookie_name not in flask.request.cookies:
            has_access = check_view_access(oauth_token, fid)
        else:
            access_cookie = flask.request.cookies[auth_cookie_name]

            # If there access was previously declined,
            # check access again in case it has changed
            if access_cookie != access_codes['access_granted']:
                has_access = check_view_access(oauth_token, fid)
            else:
                has_access = True

        if not has_access:
            return flask.Response(status=403)

        response = f(*args, **kwargs)
        # TODO - should set secure in this cookie, not exposed in flask
        response.set_cookie(
            auth_cookie_name,
            value=access_codes['access_granted'],
            max_age=(60 * 60 * 24 * 7),  # 1 week
        )
        return response
