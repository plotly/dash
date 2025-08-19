import dash
from dash import html, dcc, callback, Input, Output, clientside_callback

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
        
        # Theme Filter Row  
        html.Div([
            html.Label("Color Theme:", style={'fontWeight': '500', 'marginRight': '8px'}),
            dcc.Dropdown(
                options=[
                    {'label': 'Purple', 'value': 'purple'},
                    {'label': 'Blue', 'value': 'blue'},
                    {'label': 'Green', 'value': 'green'},
                    {'label': 'Red', 'value': 'red'},
                    {'label': 'Orange', 'value': 'orange'},
                    {'label': 'Teal', 'value': 'teal'},
                    {'label': 'Pink', 'value': 'pink'},
                    {'label': 'Indigo', 'value': 'indigo'},
                ],
                value='purple',
                id='color-theme-select',
                style={'width': '120px', 'display': 'inline-block'}
            ),
            html.Label("Scaling:", style={'fontWeight': '500', 'marginLeft': '20px', 'marginRight': '8px'}),
            dcc.Dropdown(
                options=[
                    {'label': '90%', 'value': 0.9},
                    {'label': '95%', 'value': 0.95},
                    {'label': '100%', 'value': 1.0},
                    {'label': '105%', 'value': 1.05},
                    {'label': '110%', 'value': 1.1},
                ],
                value=1.0,
                id='scaling-select',
                style={'width': '120px', 'display': 'inline-block'}
            )
        ], className="theme-filter-row", style={'alignItems': 'center'}),
        
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
                        'border': '2px solid var(--accent-8)',
                        'borderRadius': 'var(--radius-2)'
                    },
                    id='styled-dropdown'
                )
            ], className='showcase-item')
            
        ], className='showcase-grid'),
        
        html.Div([
            dcc.Link("← Back to Home", href='/', 
                    style={'display': 'inline-block', 'marginTop': '40px', 'textDecoration': 'none'})
        ]),
        
        
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '40px 20px'})
])

# Clientside callbacks for theme switching
clientside_callback(
    """
    function(color) {
        if (!color) return window.dash_clientside.no_update;
        
        console.log('Color theme changed to:', color);
        
        // Remove all existing theme classes
        document.body.classList.remove('theme-purple', 'theme-blue', 'theme-green', 'theme-red', 'theme-orange', 'theme-teal', 'theme-pink', 'theme-indigo');
        
        // Add the new theme class (CSS variables are defined in styles.css per theme)
        document.body.classList.add('theme-' + color);
        
        console.log('Applied theme class: theme-' + color);
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('basic-dropdown', 'style'),  # dummy output to a different component
    Input('color-theme-select', 'value')
)

clientside_callback(
    """
    function(scale) {
        document.documentElement.style.setProperty('--scaling', scale);
        return window.dash_clientside.no_update;
    }
    """,
    Output('multi-dropdown', 'style'),  # dummy output to a different component
    Input('scaling-select', 'value')
)