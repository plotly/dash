#!/usr/bin/env python3

import dash
from dash import Dash, dcc, html

# Create app with pages enabled
app = Dash(__name__, use_pages=True, assets_folder='assets')

# Main layout with navigation and page container
app.layout = html.Div([
    html.Header([
        html.H1("Component Showcase", style={'margin': '20px 0'}),
        html.Nav([
            html.Div([
                dcc.Link(
                    f"{page.get('name', page['module'].split('.')[-1])} - {page['path']}",
                    href=page['path'],
                    style={'display': 'block', 'padding': '10px', 'textDecoration': 'none'}
                )
                for page in dash.page_registry.values()
            ])
        ])
    ], style={'padding': '20px', 'borderBottom': '1px solid #ddd'}),
    
    # Page content goes here
    dash.page_container,
    
    # Location component for routing
    dcc.Location(id='url', refresh=False)
], style={'fontFamily': 'Arial, sans-serif'})

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)