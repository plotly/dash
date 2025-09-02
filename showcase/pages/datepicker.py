import dash
from dash import html, dcc, callback, Input, Output, clientside_callback
from datetime import datetime, timedelta

# Register this page
dash.register_page(__name__, name='Date Picker Showcase')

# Helper dates for examples
today = datetime.now()
next_week = today + timedelta(days=7)
next_month = today + timedelta(days=30)
min_allowed = today - timedelta(days=30)
max_allowed = today + timedelta(days=90)

# Sample disabled days (weekends)
disabled_days = []
current_date = today
for _ in range(14):
    if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        disabled_days.append(current_date.strftime('%Y-%m-%d'))
    current_date += timedelta(days=1)

layout = html.Div([
    html.Div([
        html.Div([
            dcc.Link("← Back to Home", href='/', 
                    style={'display': 'inline-block', 'marginBottom': '20px', 'textDecoration': 'none'})
        ]),
        html.H2("Date Picker Component Variations", style={'marginBottom': '30px'}),
        
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
            # Basic DatePickerSingle
            html.Div([
                html.H4("Basic Single Date Picker"),
                html.P("Select a single date"),
                dcc.DatePickerSingle(
                    id='basic-single-picker',
                    date=today.strftime('%Y-%m-%d'),
                    placeholder="Select a date",
                    clearable=True
                )
            ], className='showcase-item'),
            
            # DatePickerSingle with constraints
            html.Div([
                html.H4("Single Date with Constraints"),
                html.P("Min/max dates and disabled weekends"),
                dcc.DatePickerSingle(
                    id='constrained-single-picker',
                    min_date_allowed=min_allowed.strftime('%Y-%m-%d'),
                    max_date_allowed=max_allowed.strftime('%Y-%m-%d'),
                    disabled_days=disabled_days,
                    placeholder="Select weekday only",
                    clearable=True
                )
            ], className='showcase-item'),
            
            # DatePickerSingle with custom format
            html.Div([
                html.H4("Custom Display Format"),
                html.P("MM/DD/YYYY format"),
                dcc.DatePickerSingle(
                    id='formatted-single-picker',
                    date=today.strftime('%Y-%m-%d'),
                    display_format='MM/DD/YYYY',
                    placeholder="MM/DD/YYYY",
                    clearable=True
                )
            ], className='showcase-item'),
            
            # DatePickerSingle disabled
            html.Div([
                html.H4("Disabled Single Date Picker"),
                html.P("Non-interactive state"),
                dcc.DatePickerSingle(
                    id='disabled-single-picker',
                    date=today.strftime('%Y-%m-%d'),
                    disabled=True,
                    placeholder="Disabled"
                )
            ], className='showcase-item'),
            
            # Basic DatePickerRange
            html.Div([
                html.H4("Basic Date Range Picker"),
                html.P("Select start and end dates"),
                dcc.DatePickerRange(
                    id='basic-range-picker',
                    start_date=today.strftime('%Y-%m-%d'),
                    end_date=next_week.strftime('%Y-%m-%d'),
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    clearable=True
                )
            ], className='showcase-item'),
            
            # DatePickerRange with constraints
            html.Div([
                html.H4("Range with Minimum Nights"),
                html.P("At least 3 nights required"),
                dcc.DatePickerRange(
                    id='constrained-range-picker',
                    min_date_allowed=today.strftime('%Y-%m-%d'),
                    max_date_allowed=max_allowed.strftime('%Y-%m-%d'),
                    minimum_nights=3,
                    updatemode='bothdates',
                    start_date_placeholder_text="Check-in",
                    end_date_placeholder_text="Check-out",
                    clearable=True
                )
            ], className='showcase-item'),
            
            # DatePickerRange with different month format
            html.Div([
                html.H4("Custom Month Format"),
                html.P("Full month names displayed"),
                dcc.DatePickerRange(
                    id='month-format-range-picker',
                    start_date=today.strftime('%Y-%m-%d'),
                    month_format='MMMM YYYY',
                    display_format='DD MMM YYYY',
                    start_date_placeholder_text="DD MMM YYYY",
                    end_date_placeholder_text="DD MMM YYYY",
                    clearable=True
                )
            ], className='showcase-item'),
            
            # DatePickerSingle with portal
            html.Div([
                html.H4("Portal Calendar"),
                html.P("Opens in screen overlay"),
                dcc.DatePickerSingle(
                    id='portal-single-picker',
                    with_portal=True,
                    placeholder="Click to open portal",
                    clearable=True
                )
            ], className='showcase-item')
            
        ], className='showcase-grid'),
        
        
        
    ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '40px 20px'})
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
    Output('basic-single-picker', 'style'),  # dummy output to a different component
    Input('color-theme-select', 'value')
)

clientside_callback(
    """
    function(scale) {
        document.documentElement.style.setProperty('--scaling', scale);
        return window.dash_clientside.no_update;
    }
    """,
    Output('basic-range-picker', 'style'),  # dummy output to a different component
    Input('scaling-select', 'value')
)