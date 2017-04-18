import time
import unittest
import dash
import plotly
import dash_html_components as html
from dash import authentication, plotly_api
import Cookie
import mock




class LoginFlow(unittest.TestCase):
    def login_success(self):
        app = dash.Dash()
        app.layout = html.Div()
        client = app.server.test_client()
        csrf_token = get_cookie(client.get('/'), '_csrf_token')
        client.set_cookie('/', '_csrf_token', csrf_token)
        oauth_token = users['creator']['oauth_token']
        res = client.post('_login', headers={
            'Authorization': 'Bearer {}'.format(oauth_token),
            'X-CSRFToken': csrf_token
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            get_cookie(res, 'plotly_dash_oauth_token'),
            token
        )
