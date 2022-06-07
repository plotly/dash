import dash
from dash import html


dash.register_page(__name__, id="page2")

layout = html.Div("text for page2", id="text_page2")
