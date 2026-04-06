"""Reusable layout utilities for traversing and inspecting Dash component trees."""

from __future__ import annotations

import json
from typing import Any, Generator

from dash import get_app
from dash._pages import PAGE_REGISTRY
from dash.dependencies import Wildcard
from dash.development.base_component import Component

_WILDCARD_VALUES = frozenset(w.value for w in Wildcard)


def traverse(
    start: Component | None = None,
) -> Generator[tuple[Component, tuple[Component, ...]], None, None]:
    """Yield ``(component, ancestors)`` for every Component in the tree.

    If ``start`` is ``None``, the full app layout is resolved via
    ``dash.get_app()``, preferring ``validation_layout`` for completeness.
    """
    if start is None:
        app = get_app()
        start = getattr(app, "validation_layout", None) or app.get_layout()

    yield from _walk(start, ())


def _walk(
    node: Any,
    ancestors: tuple[Component, ...],
) -> Generator[tuple[Component, tuple[Component, ...]], None, None]:
    if node is None:
        return
    if isinstance(node, (list, tuple)):
        for item in node:
            yield from _walk(item, ancestors)
        return
    if not isinstance(node, Component):
        return

    yield node, ancestors

    child_ancestors = (*ancestors, node)
    for _prop_name, child in iter_children(node):
        yield from _walk(child, child_ancestors)


def iter_children(
    component: Component,
) -> Generator[tuple[str, Component], None, None]:
    """Yield ``(prop_name, child_component)`` for all component-valued props.

    Walks ``children`` plus any props declared in the component's
    ``_children_props`` list. Supports nested path expressions like
    ``control_groups[].children`` and ``insights.title``.
    """
    props_to_walk = ["children"] + getattr(component, "_children_props", [])
    for prop_path in props_to_walk:
        for child in get_children(component, prop_path):
            yield prop_path, child


def get_children(component: Any, prop_path: str) -> list[Component]:
    """Resolve a ``_children_props`` path expression to child Components.

    Mirrors the dash-renderer's path parsing in ``DashWrapper.tsx``.
    Supports:
    - ``"children"`` — simple prop
    - ``"control_groups[].children"`` — array, then sub-prop per element
    - ``"insights.title"`` — nested object prop
    """
    clean_path = prop_path.replace("[]", "").replace("{}", "")

    if "." not in prop_path:
        return _collect_components(getattr(component, clean_path, None))

    parts = prop_path.split(".")
    array_idx = next((i for i, p in enumerate(parts) if "[]" in p), len(parts))
    front = [p.replace("[]", "").replace("{}", "") for p in parts[: array_idx + 1]]
    back = [p.replace("{}", "") for p in parts[array_idx + 1 :]]

    node = _resolve_path(component, front)
    if node is None:
        return []

    if back and isinstance(node, (list, tuple)):
        results: list[Component] = []
        for element in node:
            child = _resolve_path(element, back)
            results.extend(_collect_components(child))
        return results

    return _collect_components(node)


def _resolve_path(node: Any, keys: list[str]) -> Any:
    """Walk a chain of keys through Components and dicts."""
    for key in keys:
        if isinstance(node, Component):
            node = getattr(node, key, None)
        elif isinstance(node, dict):
            node = node.get(key)
        else:
            return None
        if node is None:
            return None
    return node


def _collect_components(value: Any) -> list[Component]:
    """Extract Components from a value (single, list, or None)."""
    if value is None:
        return []
    if isinstance(value, Component):
        return [value]
    if isinstance(value, (list, tuple)):
        return [item for item in value if isinstance(item, (Component, list, tuple))]
    return []


def find_component(
    component_id: str | dict,
    layout: Component | None = None,
    page: str | None = None,
) -> Component | None:
    """Find a component by ID.

    If neither ``layout`` nor ``page`` is provided, searches the full
    app layout (preferring ``validation_layout`` for completeness).
    """
    if page is not None:
        layout = _resolve_page_layout(page)

    if layout is None:
        app = get_app()
        layout = getattr(app, "validation_layout", None) or app.get_layout()

    for comp, _ in traverse(layout):
        if getattr(comp, "id", None) == component_id:
            return comp
    return None


def parse_wildcard_id(pid: Any) -> dict | None:
    """Parse a component ID and return it as a dict if it contains a wildcard.

    Accepts string (JSON-encoded) or dict IDs. Returns ``None``
    if the ID is not a wildcard pattern.

    Example::

        >>> parse_wildcard_id('{"type":"input","index":["ALL"]}')
        {"type": "input", "index": ["ALL"]}
        >>> parse_wildcard_id("my-dropdown")
        None
    """
    if isinstance(pid, str) and pid.startswith("{"):
        try:
            pid = json.loads(pid)
        except (json.JSONDecodeError, ValueError):
            return None
    if not isinstance(pid, dict):
        return None
    for v in pid.values():
        if isinstance(v, list) and len(v) == 1 and v[0] in _WILDCARD_VALUES:
            return pid
    return None


def find_matching_components(pattern: dict) -> list[Component]:
    """Find all components whose dict ID matches a wildcard pattern.

    Non-wildcard keys must match exactly. Wildcard keys are ignored.
    """
    non_wildcard_keys = {
        k: v
        for k, v in pattern.items()
        if not (isinstance(v, list) and len(v) == 1 and v[0] in _WILDCARD_VALUES)
    }
    matches = []
    for comp, _ in traverse():
        comp_id = getattr(comp, "id", None)
        if not isinstance(comp_id, dict):
            continue
        if all(comp_id.get(k) == v for k, v in non_wildcard_keys.items()):
            matches.append(comp)
    return matches


def extract_text(component: Component) -> str:
    """Recursively extract plain text from a component's children tree.

    Mimics the browser's ``element.textContent``.
    """
    children = getattr(component, "children", None)
    if children is None:
        return ""
    if isinstance(children, str):
        return children
    if isinstance(children, Component):
        return extract_text(children)
    if isinstance(children, (list, tuple)):
        parts: list[str] = []
        for child in children:
            if isinstance(child, str):
                parts.append(child)
            elif isinstance(child, Component):
                parts.append(extract_text(child))
        return "".join(parts).strip()
    return ""


def _resolve_page_layout(page: str) -> Any | None:
    if not PAGE_REGISTRY:
        return None
    for _module, page_info in PAGE_REGISTRY.items():
        if page_info.get("path") == page:
            page_layout = page_info.get("layout")
            if callable(page_layout):
                try:
                    page_layout = page_layout()
                except (TypeError, RuntimeError):
                    return None
            return page_layout
    return None
