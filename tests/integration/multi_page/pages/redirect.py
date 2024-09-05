import dash
from dash import html


dash.register_page(__name__, redirect_from=["/old-home-page", "/v2"], id="redirect")

layout = html.Div("text for redirect", id="text_redirect")
