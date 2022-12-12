import dash
from dash import html


dash.register_page(__name__, path_template="/a/<id_a>/b/<id_b>", id="register_page")


def layout(id_a=None, id_b=None, **other_unknown_query_strings):
    return html.Div(
        [
            html.Div("text for register_page", id="text_register_page"),
            html.Div(f"variables from pathname:{id_a} {id_b}", id="path_vars"),
        ]
    )
