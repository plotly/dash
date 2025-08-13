import dash
from dash import html, dcc

# Register this page
dash.register_page(__name__, name='Dropdown Showcase')

# Sample options for dropdowns
simple_options = ['Apple', 'Banana', 'Cherry', 'Date']
complex_options = [
    {'label': 'New York City', 'value': 'NYC'},
    {'label': 'Montreal', 'value': 'MTL'},
    {'label': 'San Francisco', 'value': 'SF'},
    {'label': 'London', 'value': 'LDN', 'disabled': True}
]

layout = html.Div([
    html.Div([
        html.H2("Dropdown Component Variations", style={'marginBottom': '30px'}),
        
        # Component showcase grid
        html.Div([
            # Basic dropdown
            html.Div([
                html.H4("Basic Dropdown"),
                html.P("Simple options, single selection"),
                dcc.Dropdown(
                    options=simple_options,
                    value='Apple',
                    id='basic-dropdown'
                )
            ], className='showcase-item'),
            
            # Multi-select dropdown
            html.Div([
                html.H4("Multi-Select"),
                html.P("Allow multiple selections"),
                dcc.Dropdown(
                    options=simple_options,
                    value=['Apple', 'Cherry'],
                    multi=True,
                    id='multi-dropdown'
                )
            ], className='showcase-item'),
            
            # Searchable dropdown
            html.Div([
                html.H4("Searchable"),
                html.P("Search through options"),
                dcc.Dropdown(
                    options=complex_options,
                    searchable=True,
                    placeholder="Search cities...",
                    id='searchable-dropdown'
                )
            ], className='showcase-item'),
            
            # Clearable disabled
            html.Div([
                html.H4("Not Clearable"),
                html.P("Cannot clear selection"),
                dcc.Dropdown(
                    options=simple_options,
                    value='Banana',
                    clearable=False,
                    id='not-clearable-dropdown'
                )
            ], className='showcase-item'),
            
            # Disabled dropdown
            html.Div([
                html.H4("Disabled State"),
                html.P("Dropdown is disabled"),
                dcc.Dropdown(
                    options=simple_options,
                    value='Cherry',
                    disabled=True,
                    id='disabled-dropdown'
                )
            ], className='showcase-item'),
            
            # Custom styling
            html.Div([
                html.H4("Custom Styled"),
                html.P("Custom colors and styling"),
                dcc.Dropdown(
                    options=complex_options,
                    value='NYC',
                    style={
                        'backgroundColor': '#f0f8ff',
                        'border': '2px solid #4CAF50',
                        'borderRadius': '8px'
                    },
                    id='styled-dropdown'
                )
            ], className='showcase-item')
            
        ], className='showcase-grid'),
        
        html.Div([
            dcc.Link("← Back to Home", href='/', 
                    style={'display': 'inline-block', 'marginTop': '40px', 'textDecoration': 'none'})
        ])
        
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '40px 20px'})
])