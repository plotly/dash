"""Tests for the DataFrame tool result formatter."""

import pytest

from dash.mcp.primitives.tools.results.result_dataframe import (
    MAX_ROWS,
    format_dataframe,
)

pd = pytest.importorskip("pandas")


class TestFormatDataframe:
    def test_markdown_table_structure(self):
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        result = format_dataframe(df)
        text = result.content[0].text

        assert "| name | age |" in text
        assert "| --- | --- |" in text
        assert "| Alice | 30 |" in text
        assert "| Bob | 25 |" in text

    def test_metadata_summary(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        result = format_dataframe(df)
        text = result.content[0].text
        assert "3 rows" in text
        assert "1 columns" in text

    def test_row_cap(self):
        df = pd.DataFrame({"v": range(MAX_ROWS + 50)})
        result = format_dataframe(df)
        text = result.content[0].text

        # Should show truncation note
        assert "50 more rows" in text

        # Count data rows (lines starting with | excluding header and separator)
        lines = text.strip().split("\n")
        table_lines = [line for line in lines if line.startswith("|")]
        # header + separator + MAX_ROWS data rows
        assert len(table_lines) == MAX_ROWS + 2

    def test_pipe_escaping(self):
        df = pd.DataFrame({"val": ["a|b"]})
        result = format_dataframe(df)
        text = result.content[0].text
        assert "a\\|b" in text

    def test_result_has_single_text_content(self):
        df = pd.DataFrame({"a": [1]})
        result = format_dataframe(df)
        assert len(result.content) == 1
        assert result.content[0].type == "text"

    def test_is_error_defaults_false(self):
        df = pd.DataFrame({"a": [1]})
        result = format_dataframe(df)
        assert result.isError is False
