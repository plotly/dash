# Index file for a gallery and review app
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import review_app

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'width': '80%'
    },
    children=[
        dcc.Location(id='location'),
        html.H1('Dash Table Gallery App'),
        html.Div(id='container'),
        html.Div(
            style={'display': 'none'},
            children=dash_table.Table(id='hidden')
        )
    ]
)


@app.callback(Output('container', 'children'),
              [Input('location', 'pathname')])
def display_app(pathname):
    if pathname == '/':
        return html.Ol([
            html.Li(dcc.Link('Simple', href='/simple')),
            html.Li(dcc.Link('Multi Header', href='/multi-header')),
        ])
    if pathname == '/simple':
        return review_app.simple.layout()
    elif pathname == '/multi-header':
        return review_app.multi_header.layout()


app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

if __name__ == '__main__':
    app.run_server(debug=True)
