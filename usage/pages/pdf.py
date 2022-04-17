# Example of matching a path that ends in ".pdf"

import dash

dash.register_page(
    __name__,
    path_template="/<pdf_id>.pdf",
)


def layout(pdf_id=None):
    return dash.html.Div(f"pdf file:  {pdf_id}.pdf")
