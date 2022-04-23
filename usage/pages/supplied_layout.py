# Example of supplied layout overriding module layout

from dash import html

import dash

dash.register_page("custom_name", layout=html.Div("my custom layout"))

layout = html.Div("shouldn't be this one")

#
# from dash import html
#
# import dash
#
# dash.register_page(__name__)
#
# layout = html.Div("shouldn't be this one")
