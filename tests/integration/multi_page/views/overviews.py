import dash
from dash import html


dash.register_page(__name__)

layout = html.Div("text for overviews", id="text_overviews")
