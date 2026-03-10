"""Tests for schema_component_proptypes.

Only tests our custom logic — pydantic's type-to-schema conversion
is tested by pydantic itself.
"""

from dash.development.base_component import Component
from dash.mcp.primitives.tools.input_schemas.schema_component_proptypes import (
    get_json_schema,
)


class TestComponentTypes:
    def test_component_type_maps_to_string(self):
        assert get_json_schema(Component) == {"type": "string"}
