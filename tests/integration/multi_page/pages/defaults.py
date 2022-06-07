import dash
from dash import html


dash.register_page(__name__, id="defaults")

layout = html.Div("text for defaults", id="text_defaults")
