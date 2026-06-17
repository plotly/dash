import sys
from pathlib import Path

import pytest

from dash.development._py_components_generation import generate_class_string
from dash.development._py_prop_typing import shapes

CONDITIONAL_STYLE_TYPE = {
    "name": "arrayOf",
    "value": {
        "name": "shape",
        "value": {
            "if": {
                "name": "exact",
                "value": {
                    "column_id": {"name": "string", "required": False},
                },
                "required": False,
            },
        },
    },
}


@pytest.mark.parametrize(
    "prop_name, shape_name",
    [
        ("style_cell_conditional", "StyleCellConditional"),
        ("style_data_conditional", "StyleDataConditional"),
        ("style_filter_conditional", "StyleFilterConditional"),
        ("style_header_conditional", "StyleHeaderConditional"),
    ],
)
def test_datatable_conditional_styles_allow_style_keys(
    monkeypatch, prop_name, shape_name
):
    dash_table_dir = Path(__file__).resolve().parents[3] / "components" / "dash-table"
    monkeypatch.syspath_prepend(str(dash_table_dir))
    sys.modules.pop("dash_prop_typing", None)
    shapes.clear()

    generated = generate_class_string(
        typename="DataTable",
        props={
            prop_name: {
                "type": CONDITIONAL_STYLE_TYPE,
                "required": False,
                "description": "Conditional style",
            },
        },
        description="DataTable",
        namespace="dash_table",
        custom_typing_module="dash_prop_typing",
    )

    assert (
        f'{prop_name}: typing.Optional[typing.Sequence[typing.Union["{shape_name}", '
        "typing.Dict[str, typing.Any]]]] = None"
    ) in generated
    assert f'"if": NotRequired["{shape_name}If"]' in generated

    shapes.clear()
    sys.modules.pop("dash_prop_typing", None)
