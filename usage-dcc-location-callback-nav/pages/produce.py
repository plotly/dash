import dash


def layout(prodcode=None, **other_unknown_query_strings):
    return dash.html.Div(f"Produce dashboard for product code {prodcode}")
