import dash
from dash import html, dcc

# Register this as the home page
dash.register_page(__name__, path='/', name='Home')

layout = html.Div([
    html.Div([
        html.H2("Component Showcase", style={'textAlign': 'center', 'marginBottom': '30px'}),
        html.P("Select a component below to view different property configurations and styling options:", 
               style={'textAlign': 'center', 'marginBottom': '40px', 'color': '#666'}),
        
        html.Div([
            # Component showcase cards
            html.Div([
                dcc.Link([
                    html.Div([
                        html.H3("Dropdown", style={'margin': '0 0 10px 0'}),
                        html.P("Interactive dropdown with various options and states", 
                               style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
                    ])
                ], href='/dropdown', style={'textDecoration': 'none', 'color': 'inherit'})
            ], className='component-card'),
            
            html.Div([
                dcc.Link([
                    html.Div([
                        html.H3("Date Picker", style={'margin': '0 0 10px 0'}),
                        html.P("Single and range date pickers with calendar interface", 
                               style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
                    ])
                ], href='/datepicker', style={'textDecoration': 'none', 'color': 'inherit'})
            ], className='component-card'),
            
            html.Div([
                dcc.Link([
                    html.Div([
                        html.H3("Slider", style={'margin': '0 0 10px 0'}),
                        html.P("Range sliders with various configurations and orientations", 
                               style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
                    ])
                ], href='/slider', style={'textDecoration': 'none', 'color': 'inherit'})
            ], className='component-card')
            
        ], className='component-grid')
        
    ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '40px 20px'})
])