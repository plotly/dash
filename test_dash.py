#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash import Dash, html, dcc

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Test App"),
    html.P("If you can see this, Dash is working!")
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)