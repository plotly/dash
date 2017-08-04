import dash
import dash_html_components as html
import dash_core_components as dcc

app = dash.Dash()
app.layout = html.Div([
    dcc.Dropdown(options=[{'label': 'Option ' + str(i), 'value': i} for i in range(23 * 1000)], multi=True)
])

app.scripts.config.serve_locally=True

if __name__ == '__main__':
    app.run_server(debug=True, port=8090)
