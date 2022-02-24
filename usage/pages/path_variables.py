import dash


def title(asset_id=None, dept_id=None):
    return f"Asset Analysis: {asset_id} {dept_id}"


def description(asset_id=None, dept_id=None):
    return f"This is the AVN Industries Asset Analysis: {asset_id} in {dept_id}"


dash.register_page(
    __name__,
    path_template="/asset/<asset_id>/department/<dept_id>",
    title=title,
    description=description,
    path="/asset/inventory/department/branch-1001",
)


def layout(asset_id=None, dept_id=None, **other_unknown_query_strings):
    return dash.html.Div(
        f"variables from pathname:  asset_id: {asset_id} dept_id: {dept_id}"
    )
