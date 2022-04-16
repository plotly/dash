import dash



dash.register_page(
    __name__,
    path_template="/goto-<data>-and-<data2>-data",
    path="/goto-br1-and-br2-data",
)


def layout(data=None, data2=None):
    return dash.html.Div(f"goto:  {data}-{data2}")
