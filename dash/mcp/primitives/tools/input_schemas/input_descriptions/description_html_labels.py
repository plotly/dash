"""Label-based property descriptions.

Reads the label map from the ``CallbackAdapterCollection``,
which builds it from the layout using ``htmlFor`` and
containment associations.
"""

from __future__ import annotations

from dash import get_app
from dash.mcp.types import MCPInput


def label_description(param: MCPInput) -> list[str]:
    """Return the label text for this component, if any."""
    component_id = param.get("component_id")
    if not component_id:
        return []
    label_map = get_app().mcp_callback_map.component_label_map
    texts = label_map.get(component_id, [])
    if texts:
        return [f"Labeled with: {'; '.join(texts)}"]
    return []
