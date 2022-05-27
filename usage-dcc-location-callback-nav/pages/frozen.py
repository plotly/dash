import dash


def layout(prodcode=None, **other_unknown_query_strings):
    return dash.html.Div(f"Frozen Food dashboard for product code {prodcode}")
