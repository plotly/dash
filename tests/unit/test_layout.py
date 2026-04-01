"""Tests for dash.layout — layout traversal and component lookup utilities."""

import pytest

from dash import html, dcc
from dash.layout import (
    traverse,
    find_component,
    extract_text,
    parse_wildcard_id,
)


@pytest.fixture
def sample_layout():
    return html.Div(
        [
            html.Label("Name:", htmlFor="name-input"),
            " ",
            dcc.Input(id="name-input", value="World"),
            html.Div(
                [html.Span(id="deep-child", children="deep text")],
                id="inner",
            ),
        ],
        id="root",
    )


class TestTraverse:
    def test_yields_all_components_with_correct_ancestors(self, sample_layout):
        results = {
            getattr(c, "id", None): len(ancestors)
            for c, ancestors in traverse(sample_layout)
        }
        assert results["root"] == 0
        assert results["name-input"] == 1
        assert results["deep-child"] == 2

    def test_empty_layout(self):
        results = list(traverse(html.Div()))
        assert len(results) == 1  # just the Div itself


class TestFindComponent:
    def test_finds_by_string_id(self, sample_layout):
        comp = find_component("deep-child", layout=sample_layout)
        assert comp is not None and comp.id == "deep-child"

    def test_returns_none_for_missing_id(self, sample_layout):
        assert find_component("nope", layout=sample_layout) is None

    def test_finds_by_dict_id(self):
        layout = html.Div([html.Div(id={"type": "item", "index": 0})])
        assert find_component({"type": "item", "index": 0}, layout=layout) is not None


class TestExtractText:
    def test_extracts_all_text_content(self, sample_layout):
        assert extract_text(sample_layout) == "Name: deep text"

    def test_none_children(self):
        assert extract_text(html.Div()) == ""


class TestParseWildcardId:
    @pytest.mark.parametrize("wildcard", ["ALL", "MATCH", "ALLSMALLER"])
    def test_returns_dict_for_wildcard(self, wildcard):
        result = parse_wildcard_id({"type": "input", "index": [wildcard]})
        assert result == {"type": "input", "index": [wildcard]}

    def test_parses_json_string(self):
        result = parse_wildcard_id('{"type":"input","index":["ALL"]}')
        assert result == {"type": "input", "index": ["ALL"]}

    def test_returns_none_for_plain_string(self):
        assert parse_wildcard_id("my-dropdown") is None

    def test_returns_none_for_non_wildcard_dict(self):
        assert parse_wildcard_id({"type": "input", "index": 0}) is None

    def test_returns_none_for_invalid_json(self):
        assert parse_wildcard_id("{not valid}") is None
