import dash


dash.register_page(
    __name__,
    path_template="snapshot-<snapshot_id>",
    separator="snapshot-",
    path="/snapshot-0-0",
)


def layout(snapshot_id=None):
    return dash.html.Div(f"snapshot page:  snapshot-{snapshot_id}")
