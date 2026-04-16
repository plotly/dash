"""Tests for the tabular data result formatter."""

from dash.mcp.primitives.tools.results.result_dataframe import (
    MAX_ROWS,
    DataFrameResult,
)

EXPECTED_TABLE = (
    "*2 rows \u00d7 2 columns*\n"
    "\n"
    "| name | age |\n"
    "| --- | --- |\n"
    "| Alice | 30 |\n"
    "| Bob | 25 |"
)

SAMPLE_ROWS = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

DATATABLE_OUTPUT = {
    "component_type": "DataTable",
    "property": "data",
    "component_id": "t",
    "id_and_prop": "t.data",
    "initial_value": None,
    "tool_name": "update",
}

AGGRID_OUTPUT = {
    "component_type": "AgGrid",
    "property": "rowData",
    "component_id": "g",
    "id_and_prop": "g.rowData",
    "initial_value": None,
    "tool_name": "update",
}


class TestDataframeResult:
    def test_datatable_data_renders_markdown(self):
        result = DataFrameResult.format(DATATABLE_OUTPUT, SAMPLE_ROWS)
        assert len(result) == 1
        assert result[0].text == EXPECTED_TABLE

    def test_aggrid_rowdata_renders_markdown(self):
        result = DataFrameResult.format(AGGRID_OUTPUT, SAMPLE_ROWS)
        assert len(result) == 1
        assert result[0].text == EXPECTED_TABLE

    def test_ignores_non_tabular_props(self):
        non_tabular = {**DATATABLE_OUTPUT, "property": "columns"}
        assert DataFrameResult.format(non_tabular, SAMPLE_ROWS) == []

    def test_ignores_empty_or_non_dict_rows(self):
        assert DataFrameResult.format(DATATABLE_OUTPUT, []) == []
        assert DataFrameResult.format(DATATABLE_OUTPUT, ["a", "b"]) == []

    def test_truncates_large_tables(self):
        rows = [{"i": n} for n in range(MAX_ROWS + 50)]
        result = DataFrameResult.format(DATATABLE_OUTPUT, rows)
        text = result[0].text
        assert f"| {MAX_ROWS - 1} |" in text
        assert f"| {MAX_ROWS} |" not in text
        assert "50 more rows" in text
