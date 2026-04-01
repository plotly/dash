"""Tests for dash.types — Pydantic-compatible types and schemas."""

from pydantic import TypeAdapter

from dash.types import NumberType, CallbackDispatchBody, CallbackDispatchResponse
from dash.development.base_component import Component


class TestNumberType:
    def test_json_schema_is_number(self):
        schema = TypeAdapter(NumberType).json_schema()
        assert schema["type"] == "number"


class TestComponentPydanticSchema:
    def test_produces_object_schema(self):
        schema = TypeAdapter(Component).json_schema()
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_schema_has_type_and_props(self):
        schema = TypeAdapter(Component).json_schema()
        props = schema["properties"]
        assert "type" in props
        assert "props" in props


class TestCallbackDispatchTypes:
    def test_dispatch_body_schema(self):
        schema = TypeAdapter(CallbackDispatchBody).json_schema()
        assert "output" in schema["properties"]
        assert "inputs" in schema["properties"]

    def test_dispatch_response_schema(self):
        schema = TypeAdapter(CallbackDispatchResponse).json_schema()
        assert "response" in schema["properties"]
