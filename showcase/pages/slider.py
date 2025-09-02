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
            ),
            html.Label("Tick Marks:", style={'fontWeight': '500', 'marginLeft': '20px', 'marginRight': '8px'}),
            dcc.Dropdown(
                options=[
                    {'label': 'Hide', 'value': 'hide'},
                    {'label': 'Show', 'value': 'show'},
                ],
                value='hide',
                id='tick-marks-select',
                style={'width': '120px', 'display': 'inline-block'}
            )
        ], className="theme-filter-row", style={'alignItems': 'center'}),
        
        # Component showcase grid
        html.Div([
            # Basic slider
            html.Div([
                html.H4("Basic Slider"),
                html.P("Simple range slider with default settings"),
                # Header row: Range label and Reset value
                html.Div([
                    html.Div([
                        html.Span("Range", className='range-label'),
                        html.Span("ⓘ", className='info-icon')
                    ], className='range-label-container'),
                    html.A("Reset value", href="#", id='basic-slider-reset', className='reset-link')
                ], className='slider-header'),
                # Slider row: Input LEFT, Slider RIGHT
                html.Div([
                    dcc.Input(
                        type='text',
                        value='50',
                        id='basic-slider-input',
                        className='slider-text-input',
                        debounce=True
                    ),
                    html.Div([
                        dcc.Slider(
                            min=0,
                            max=100,
                            step=10,
                            value=50,
                            id='basic-slider'
                        )
                    ], className='slider-wrapper')
                ], className='slider-input-container'),
                html.Div(id='basic-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Stepped slider with dots
            html.Div([
                html.H4("Stepped with Dots"),
                html.P("Defined step increments with visible dots"),
                # Header row: Range label and Reset value
                html.Div([
                    html.Div([
                        html.Span("Range", className='range-label'),
                        html.Span("ⓘ", className='info-icon')
                    ], className='range-label-container'),
                    html.A("Reset value", href="#", id='stepped-slider-reset', className='reset-link')
                ], className='slider-header'),
                # Slider row: Input LEFT, Slider RIGHT
                html.Div([
                    dcc.Input(
                        type='text',
                        value='10',
                        id='stepped-slider-input',
                        className='slider-text-input',
                        debounce=True
                    ),
                    html.Div([
                        dcc.Slider(
                            min=0,
                            max=20,
                            step=5,
                            value=10,
                            dots=True,
                            id='stepped-slider'
                        )
                    ], className='slider-wrapper')
                ], className='slider-input-container'),
                html.Div(id='stepped-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Custom marks slider
            html.Div([
                html.H4("Custom Marks"),
                html.P("Slider with custom labels at specific points"),
                # Header row: Range label and Reset value
                html.Div([
                    html.Div([
                        html.Span("Range", className='range-label'),
                        html.Span("ⓘ", className='info-icon')
                    ], className='range-label-container'),
                    html.A("Reset value", href="#", id='marks-slider-reset', className='reset-link')
                ], className='slider-header'),
                # Slider row: Input LEFT, Slider RIGHT
                html.Div([
                    dcc.Input(
                        type='text',
                        value='5',
                        id='marks-slider-input',
                        className='slider-text-input',
                        debounce=True
                    ),
                    html.Div([
                        dcc.Slider(
                            min=0,
                            max=10,
                            step=None,
                            value=5,
                            id='marks-slider'
                        )
                    ], className='slider-wrapper')
                ], className='slider-input-container'),
                html.Div(id='marks-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Range slider
            html.Div([
                html.H4("Range Slider"),
                html.P("Multi-handle slider for selecting ranges"),
                # Header row: Range label and Reset value
                html.Div([
                    html.Div([
                        html.Span("Range", className='range-label'),
                        html.Span("ⓘ", className='info-icon')
                    ], className='range-label-container'),
                    html.A("Reset value", href="#", id='range-slider-reset', className='reset-link')
                ], className='slider-header'),
                # Slider row: Min Input LEFT, Slider CENTER, Max Input RIGHT
                html.Div([
                    dcc.Input(
                        type='text',
                        value='20',
                        id='range-slider-min-input',
                        className='slider-text-input',
                        debounce=True
                    ),
                    html.Div([
                        dcc.RangeSlider(
                            min=0,
                            max=100,
                            value=[20, 80],
                            id='range-slider'
                        )
                    ], className='slider-wrapper'),
                    dcc.Input(
                        type='text',
                        value='80',
                        id='range-slider-max-input',
                        className='slider-text-input',
                        debounce=True
                    )
                ], className='range-slider-container'),
                html.Div(id='range-slider-output', style={'marginTop': '10px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            
            # Disabled slider
            html.Div([
                html.H4("Disabled State"),
                html.P("Non-interactive disabled slider"),
                # Header row: Range label and Reset value
                html.Div([
                    html.Div([
                        html.Span("Range", className='range-label'),
                        html.Span("ⓘ", className='info-icon')
                    ], className='range-label-container'),
                    html.A("Reset value", href="#", id='disabled-slider-reset', className='reset-link')
                ], className='slider-header'),
                # Slider row: Input LEFT, Slider RIGHT
                html.Div([
                    dcc.Input(
                        type='text',
                        value='70',
                        id='disabled-slider-input',
                        className='slider-text-input',
                        disabled=True
                    ),
                    html.Div([
                        dcc.Slider(
                            min=0,
                            max=100,
                            step=10,
                            value=70,
                            disabled=True,
                            id='disabled-slider'
                        )
                    ], className='slider-wrapper')
                ], className='slider-input-container'),
                html.Div("Value: 70 (disabled)", style={'marginTop': '10px', 'fontSize': '14px', 'color': '#999'})
            ], className='showcase-item'),
            
            # Tooltip variations
            html.Div([
                html.H4("Tooltip Always Visible"),
                html.P("Tooltip placement and visibility options"),
                # Header row: Range label and Reset value
                html.Div([
                    html.Div([
                        html.Span("Range", className='range-label'),
                        html.Span("ⓘ", className='info-icon')
                    ], className='range-label-container'),
                    html.A("Reset value", href="#", id='tooltip-slider-reset', className='reset-link')
                ], className='slider-header'),
                # Slider row: Input LEFT, Slider RIGHT
                html.Div([
                    dcc.Input(
                        type='text',
                        value='65',
                        id='tooltip-slider-input',
                        className='slider-text-input',
                        debounce=True
                    ),
                    html.Div([
                        dcc.Slider(
                            min=0,
                            max=100,
                            step=5,
                            value=65,
                            tooltip={
                                "placement": "bottom", 
                                "always_visible": True,
                                "style": {"backgroundColor": "var(--accent-9)", "color": "white"}
                            },
                            id='tooltip-slider'
                        )
                    ], className='slider-wrapper')
                ], className='slider-input-container'),
                html.Div(id='tooltip-slider-output', style={'marginTop': '20px', 'fontSize': '14px'})
            ], className='showcase-item'),
            
            # Update mode comparison
            html.Div([
                html.H4("Update on Drag"),
                html.P("Continuously updates during dragging"),
                # Header row: Range label and Reset value
                html.Div([
                    html.Div([
                        html.Span("Range", className='range-label'),
                        html.Span("ⓘ", className='info-icon')
                    ], className='range-label-container'),
                    html.A("Reset value", href="#", id='drag-slider-reset', className='reset-link')
                ], className='slider-header'),
                # Slider row: Input LEFT, Slider RIGHT
                html.Div([
                    dcc.Input(
                        type='text',
                        value='40',
                        id='drag-slider-input',
                        className='slider-text-input',
                        debounce=True
                    ),
                    html.Div([
                        dcc.Slider(
                            min=0,
                            max=100,
                            step=5,
                            value=40,
                            updatemode='drag',
                            id='drag-slider'
                        )
                    ], className='slider-wrapper')
                ], className='slider-input-container'),
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

@callback(Output('tooltip-slider-output', 'children'), Input('tooltip-slider', 'value'))
def update_tooltip_output(value):
    return f"Value: {value}"

@callback(Output('drag-slider-output', 'children'), Input('drag-slider', 'value'))
def update_drag_output(value):
    return f"Value: {value} (updates on drag)"

# Bidirectional sync callbacks for single sliders (text inputs)
@callback(
    Output('basic-slider-input', 'value'),
    Input('basic-slider', 'value')
)
def sync_basic_slider_to_input(slider_value):
    return str(slider_value) if slider_value is not None else '0'

@callback(
    Output('basic-slider', 'value'),
    Input('basic-slider-input', 'value'),
    prevent_initial_call=True
)
def sync_basic_input_to_slider(input_value):
    if input_value is None or input_value == '':
        return dash.no_update
    try:
        val = float(input_value)
        return max(0, min(100, val))
    except (ValueError, TypeError):
        return dash.no_update

@callback(
    Output('stepped-slider-input', 'value'),
    Input('stepped-slider', 'value')
)
def sync_stepped_slider_to_input(slider_value):
    return str(slider_value) if slider_value is not None else '0'

@callback(
    Output('stepped-slider', 'value'),
    Input('stepped-slider-input', 'value'),
    prevent_initial_call=True
)
def sync_stepped_input_to_slider(input_value):
    if input_value is None or input_value == '':
        return dash.no_update
    try:
        val = float(input_value)
        return max(0, min(20, val))
    except (ValueError, TypeError):
        return dash.no_update

@callback(
    Output('marks-slider-input', 'value'),
    Input('marks-slider', 'value')
)
def sync_marks_slider_to_input(slider_value):
    return str(slider_value) if slider_value is not None else '0'

@callback(
    Output('marks-slider', 'value'),
    Input('marks-slider-input', 'value'),
    prevent_initial_call=True
)
def sync_marks_input_to_slider(input_value):
    if input_value is None or input_value == '':
        return dash.no_update
    try:
        val = float(input_value)
        return max(0, min(10, val))
    except (ValueError, TypeError):
        return dash.no_update

@callback(
    Output('tooltip-slider-input', 'value'),
    Input('tooltip-slider', 'value')
)
def sync_tooltip_slider_to_input(slider_value):
    return str(slider_value) if slider_value is not None else '0'

@callback(
    Output('tooltip-slider', 'value'),
    Input('tooltip-slider-input', 'value'),
    prevent_initial_call=True
)
def sync_tooltip_input_to_slider(input_value):
    if input_value is None or input_value == '':
        return dash.no_update
    try:
        val = float(input_value)
        return max(0, min(100, val))
    except (ValueError, TypeError):
        return dash.no_update

@callback(
    Output('drag-slider-input', 'value'),
    Input('drag-slider', 'value')
)
def sync_drag_slider_to_input(slider_value):
    return str(slider_value) if slider_value is not None else '0'

@callback(
    Output('drag-slider', 'value'),
    Input('drag-slider-input', 'value'),
    prevent_initial_call=True
)
def sync_drag_input_to_slider(input_value):
    if input_value is None or input_value == '':
        return dash.no_update
    try:
        val = float(input_value)
        return max(0, min(100, val))
    except (ValueError, TypeError):
        return dash.no_update

# Bidirectional sync callbacks for range slider (text inputs)
@callback(
    [Output('range-slider-min-input', 'value'),
     Output('range-slider-max-input', 'value')],
    Input('range-slider', 'value')
)
def sync_range_slider_to_inputs(range_value):
    if range_value is None:
        return '0', '100'
    return str(range_value[0]), str(range_value[1])

@callback(
    Output('range-slider', 'value'),
    [Input('range-slider-min-input', 'value'),
     Input('range-slider-max-input', 'value')],
    prevent_initial_call=True
)
def sync_range_inputs_to_slider(min_value, max_value):
    if min_value is None or max_value is None or min_value == '' or max_value == '':
        return dash.no_update
    
    try:
        min_val = float(min_value)
        max_val = float(max_value)
        
        # Ensure within bounds
        min_val = max(0, min(100, min_val))
        max_val = max(0, min(100, max_val))
        
        # Ensure min <= max
        if min_val > max_val:
            ctx = dash.callback_context
            if ctx.triggered:
                prop_id = ctx.triggered[0]['prop_id']
                if 'min-input' in prop_id:
                    max_val = min_val  # Adjust max to match min
                else:
                    min_val = max_val  # Adjust min to match max
        
        return [min_val, max_val]
    except (ValueError, TypeError):
        return dash.no_update

# Reset functionality callbacks
@callback(
    [Output('basic-slider', 'value', allow_duplicate=True),
     Output('basic-slider-input', 'value', allow_duplicate=True)],
    Input('basic-slider-reset', 'n_clicks'),
    prevent_initial_call=True
)
def reset_basic_slider(n_clicks):
    if n_clicks:
        return 50, '50'
    return dash.no_update, dash.no_update

@callback(
    [Output('stepped-slider', 'value', allow_duplicate=True),
     Output('stepped-slider-input', 'value', allow_duplicate=True)],
    Input('stepped-slider-reset', 'n_clicks'),
    prevent_initial_call=True
)
def reset_stepped_slider(n_clicks):
    if n_clicks:
        return 10, '10'
    return dash.no_update, dash.no_update

@callback(
    [Output('marks-slider', 'value', allow_duplicate=True),
     Output('marks-slider-input', 'value', allow_duplicate=True)],
    Input('marks-slider-reset', 'n_clicks'),
    prevent_initial_call=True
)
def reset_marks_slider(n_clicks):
    if n_clicks:
        return 5, '5'
    return dash.no_update, dash.no_update

@callback(
    [Output('range-slider', 'value', allow_duplicate=True),
     Output('range-slider-min-input', 'value', allow_duplicate=True),
     Output('range-slider-max-input', 'value', allow_duplicate=True)],
    Input('range-slider-reset', 'n_clicks'),
    prevent_initial_call=True
)
def reset_range_slider(n_clicks):
    if n_clicks:
        return [20, 80], '20', '80'
    return dash.no_update, dash.no_update, dash.no_update

@callback(
    [Output('tooltip-slider', 'value', allow_duplicate=True),
     Output('tooltip-slider-input', 'value', allow_duplicate=True)],
    Input('tooltip-slider-reset', 'n_clicks'),
    prevent_initial_call=True
)
def reset_tooltip_slider(n_clicks):
    if n_clicks:
        return 65, '65'
    return dash.no_update, dash.no_update

@callback(
    [Output('drag-slider', 'value', allow_duplicate=True),
     Output('drag-slider-input', 'value', allow_duplicate=True)],
    Input('drag-slider-reset', 'n_clicks'),
    prevent_initial_call=True
)
def reset_drag_slider(n_clicks):
    if n_clicks:
        return 40, '40'
    return dash.no_update, dash.no_update

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

# Tick marks toggle functionality
clientside_callback(
    """
    function(tickMarksValue) {
        if (!tickMarksValue) return window.dash_clientside.no_update;
        
        console.log('Tick marks setting changed to:', tickMarksValue);
        
        // Define marks for different sliders with max 6 marks limit
        const basicMarks = tickMarksValue === 'show' ? {0: '0', 20: '20', 40: '40', 60: '60', 80: '80', 100: '100'} : null;
        const steppedMarks = tickMarksValue === 'show' ? {0: '0', 5: '5', 10: '10', 15: '15', 20: '20'} : null;
        const rangeMarks = tickMarksValue === 'show' ? {0: '0', 25: '25', 50: '50', 75: '75', 100: '100'} : null;
        const disabledMarks = tickMarksValue === 'show' ? {0: '0', 20: '20', 40: '40', 60: '60', 80: '80', 100: '100'} : null;
        const tooltipMarks = tickMarksValue === 'show' ? {0: '0', 20: '20', 40: '40', 60: '60', 80: '80', 100: '100'} : null;
        const dragMarks = tickMarksValue === 'show' ? {0: '0', 20: '20', 40: '40', 60: '60', 80: '80', 100: '100'} : null;
        
        // Keep custom marks slider as is (preserve temperature labels)
        const customMarks = tickMarksValue === 'show' ? {
            0: '0°C',
            3: '3°C',
            5: {'label': '5°C', 'style': {'color': 'var(--accent-9)'}},
            7: '7°C',
            10: '10°C'
        } : null;
        
        return [basicMarks, steppedMarks, customMarks, rangeMarks, disabledMarks, tooltipMarks, dragMarks];
    }
    """,
    [Output('basic-slider', 'marks'),
     Output('stepped-slider', 'marks'),
     Output('marks-slider', 'marks'),
     Output('range-slider', 'marks'),
     Output('disabled-slider', 'marks'),
     Output('tooltip-slider', 'marks'),
     Output('drag-slider', 'marks')],
    Input('tick-marks-select', 'value')
)