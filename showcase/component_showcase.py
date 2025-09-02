#!/usr/bin/env python3

import dash
from dash import Dash, dcc, html

# Create app with pages enabled
app = Dash(__name__, use_pages=True, assets_folder='assets')

# Main layout with navigation and page container
app.layout = html.Div([
    # Page content goes here
    dash.page_container,
    
    # Location component for routing
    dcc.Location(id='url', refresh=False)
], style={'fontFamily': 'Arial, sans-serif'})

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)