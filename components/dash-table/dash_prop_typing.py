# This file is automatically loaded on build time to generate types.

from dash.development._py_prop_typing import get_prop_typing


def generate_conditional_style(type_info, component_name, prop_name):
    condition_type = get_prop_typing(
        type_info["value"]["name"],
        component_name,
        prop_name,
        type_info["value"],
    )
    return (
        "typing.Sequence["
        f"typing.Union[{condition_type}, typing.Dict[str, typing.Any]]"
        "]"
    )


custom_props = {
    "DataTable": {
        "style_cell_conditional": generate_conditional_style,
        "style_data_conditional": generate_conditional_style,
        "style_filter_conditional": generate_conditional_style,
        "style_header_conditional": generate_conditional_style,
    },
}
