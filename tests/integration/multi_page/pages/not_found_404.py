from dash import html
import dash

dash.register_page(__name__, path="/404", id="not_found_404")


layout = html.Div("text for not_found_404", id="text_not_found_404")
