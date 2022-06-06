import dash
from dash import html

dash.register_page(
    __name__,
    title="Supplied Title",
    description="This is the supplied description",
    name="Supplied name",
    path="/supplied-path",
    image="birds.jpeg",
    id="metas",
)


def layout():
    return html.Div("text for metas", id="text_metas")
