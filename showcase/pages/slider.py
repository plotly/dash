import dash
from dash import html, dcc, callback, Input, Output, clientside_callback

# Register this page
dash.register_page(__name__, name='Slider Showcase')

layout = html.Div([
    html.Div([
        html.Div([
            dcc.Link("← Back to Home", href='/', 
                    style={'display': 'inline-block', 'marginBottom': '20px', 'textDecoration': 'none'})
        ]),
        html.H2("Slider Component Variations", style={'marginBottom': '30px'}),
        
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
            # Basic slider
            html.Div([
                html.H4("Basic Slider"),
                html.P("Simple range slider with default settings"),
                dcc.Slider(
                    min=0,
                    max=100,
                    step=1,
                    value=50,
                    id='basic-slider'
                ),
                html.Div(id='basic-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Stepped slider with dots
            html.Div([
                html.H4("Stepped with Dots"),
                html.P("Defined step increments with visible dots"),
                dcc.Slider(
                    min=0,
                    max=20,
                    step=5,
                    value=10,
                    dots=True,
                    id='stepped-slider'
                ),
                html.Div(id='stepped-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Custom marks slider
            html.Div([
                html.H4("Custom Marks"),
                html.P("Slider with custom labels at specific points"),
                dcc.Slider(
                    min=0,
                    max=10,
                    step=None,
                    marks={
                        0: '0°C',
                        3: '3°C',
                        5: {'label': '5°C', 'style': {'color': 'var(--accent-9)'}},
                        7: '7°C',
                        10: '10°C'
                    },
                    value=5,
                    id='marks-slider'
                ),
                html.Div(id='marks-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Range slider
            html.Div([
                html.H4("Range Slider"),
                html.P("Multi-handle slider for selecting ranges"),
                dcc.RangeSlider(
                    min=0,
                    max=100,
                    step=1,
                    marks={0: '0', 25: '25', 50: '50', 75: '75', 100: '100'},
                    value=[20, 80],
                    id='range-slider'
                ),
                html.Div(id='range-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Vertical slider
            html.Div([
                html.H4("Vertical Orientation"),
                html.P("Vertically oriented slider"),
                html.Div([
                    dcc.Slider(
                        min=0,
                        max=100,
                        step=1,
                        value=30,
                        vertical=True,
                        verticalHeight=150,
                        id='vertical-slider'
                    )
                ], style={'height': '200px', 'display': 'flex', 'justifyContent': 'center'}),
                html.Div(id='vertical-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Disabled slider
            html.Div([
                html.H4("Disabled State"),
                html.P("Non-interactive disabled slider"),
                dcc.Slider(
                    min=0,
                    max=100,
                    step=1,
                    value=75,
                    disabled=True,
                    id='disabled-slider'
                ),
                html.Div("Value: 75 (disabled)", style={'marginTop': '10px', 'fontSize': '14px', 'color': '#999'})
            ], className='showcase-item'),
            
            # Tooltip variations
            html.Div([
                html.H4("Tooltip Always Visible"),
                html.P("Tooltip placement and visibility options"),
                dcc.Slider(
                    min=0,
                    max=100,
                    step=1,
                    value=65,
                    tooltip={
                        "placement": "bottom", 
                        "always_visible": True,
                        "style": {"backgroundColor": "var(--accent-9)", "color": "white"}
                    },
                    id='tooltip-slider'
                ),
                html.Div(id='tooltip-slider-output', style={'marginTop': '20px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Update mode comparison
            html.Div([
                html.H4("Update on Drag"),
                html.P("Continuously updates during dragging"),
                dcc.Slider(
                    min=0,
                    max=100,
                    step=1,
                    value=40,
                    updatemode='drag',
                    id='drag-slider'
                ),
                html.Div(id='drag-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item')
            
        ], className='showcase-grid'),
        
        
        
    ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '40px 20px'})
])

# Callbacks for slider value outputs
@callback(Output('basic-slider-output', 'children'), Input('basic-slider', 'value'))
def update_basic_output(value):
    return f"Value: {value}"

@callback(Output('stepped-slider-output', 'children'), Input('stepped-slider', 'value'))
def update_stepped_output(value):
    return f"Value: {value}"

@callback(Output('marks-slider-output', 'children'), Input('marks-slider', 'value'))
def update_marks_output(value):
    return f"Temperature: {value}°C"

@callback(Output('range-slider-output', 'children'), Input('range-slider', 'value'))
def update_range_output(value):
    return f"Range: {value[0]} - {value[1]}"

@callback(Output('vertical-slider-output', 'children'), Input('vertical-slider', 'value'))
def update_vertical_output(value):
    return f"Value: {value}"

@callback(Output('tooltip-slider-output', 'children'), Input('tooltip-slider', 'value'))
def update_tooltip_output(value):
    return f"Value: {value}"

@callback(Output('drag-slider-output', 'children'), Input('drag-slider', 'value'))
def update_drag_output(value):
    return f"Value: {value} (updates on drag)"

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
    Output('basic-slider', 'style'),  # dummy output to a different component
    Input('color-theme-select', 'value')
)

clientside_callback(
    """
    function(scale) {
        document.documentElement.style.setProperty('--scaling', scale);
        return window.dash_clientside.no_update;
    }
    """,
    Output('stepped-slider', 'style'),  # dummy output to a different component
    Input('scaling-select', 'value')
)