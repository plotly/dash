"""Collection of CallbackAdapters with cross-adapter queries.

Stored as a singleton on ``app.mcp_callback_map``.
"""

from __future__ import annotations

import hashlib
import re
from functools import cached_property
from typing import Any

from mcp.types import Tool

from dash import get_app
from dash._utils import clean_property_name, split_callback_id
from dash.layout import extract_text, find_component, traverse
from .callback_adapter import CallbackAdapter


class CallbackAdapterCollection:
    def __init__(self, app):
        callback_map = getattr(app, "callback_map", {})

        raw: list[tuple[str, dict]] = []
        for output_id, cb_info in callback_map.items():
            if cb_info.get("mcp_enabled") is False:
                continue
            if "callback" not in cb_info:
                continue
            raw.append((output_id, cb_info))

        self._tool_names_map = self._build_tool_names(raw)
        self._callbacks = [
            CallbackAdapter(callback_output_id=output_id)
            for output_id in self._tool_names_map
        ]
        # TODO: enable_mcp_server() will replace this with a direct assignment on app
        app.mcp_callback_map = self

    @staticmethod
    def _sanitize_name(name: str) -> str:

        max_len = 64
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        sanitized = re.sub(r"_+", "_", sanitized).strip("_")
        if sanitized and sanitized[0].isdigit():
            sanitized = "cb_" + sanitized
        full = sanitized or "unnamed_callback"
        if len(full) <= max_len:
            return full
        hash_suffix = hashlib.sha256(full.encode()).hexdigest()[:8]
        truncated = sanitized[: max_len - 9].rstrip("_")
        return f"{truncated}_{hash_suffix}"

    @classmethod
    def _build_tool_names(cls, raw: list[tuple[str, dict]]) -> dict[str, str]:
        func_name_counts: dict[str, int] = {}
        for _output_id, cb_info in raw:
            func = cb_info.get("callback")
            original = getattr(func, "__wrapped__", func)
            fn = getattr(original, "__name__", "") or ""
            func_name_counts[fn] = func_name_counts.get(fn, 0) + 1

        name_map: dict[str, str] = {}
        for output_id, cb_info in raw:
            func = cb_info.get("callback")
            original = getattr(func, "__wrapped__", func)
            fn = getattr(original, "__name__", "") or ""
            raw_name = fn if fn and func_name_counts[fn] == 1 else output_id
            name_map[output_id] = cls._sanitize_name(raw_name)
        return name_map

    def __iter__(self):
        return iter(self._callbacks)

    def __len__(self):
        return len(self._callbacks)

    def __getitem__(self, index):
        return self._callbacks[index]

    def find_by_tool_name(self, name: str) -> CallbackAdapter | None:
        for cb in self._callbacks:
            if cb.tool_name == name:
                return cb
        return None

    def find_by_output(self, id_and_prop: str) -> CallbackAdapter | None:
        """Find the adapter that outputs to ``id_and_prop`` (``"component_id.property"``)."""
        for cb in self._callbacks:
            try:
                parsed = split_callback_id(cb.output_id)
            except ValueError:
                continue
            if isinstance(parsed, dict):
                parsed = [parsed]
            for p in parsed:
                if f"{p['id']}.{clean_property_name(p['property'])}" == id_and_prop:
                    return cb
        return None

    def get_initial_value(self, id_and_prop: str) -> Any:
        """Return the initial value for ``id_and_prop`` (``"component_id.property"``).

        If a callback outputs to this property, runs it (recursively
        resolving its inputs). Otherwise returns the layout default.
        """
        upstream_cb = self.find_by_output(id_and_prop)
        if upstream_cb is not None:
            return upstream_cb.initial_output_value(id_and_prop)
        else:
            component_id, prop = id_and_prop.rsplit(".", 1)
            layout_component = find_component(component_id)
            return getattr(layout_component, prop, None)

    def as_mcp_tools(self) -> list[Tool]:
        """Stub — will be implemented in a future PR."""
        raise NotImplementedError("as_mcp_tools will be implemented in a future PR.")

    @property
    def tool_names(self) -> set[str]:
        return set(self._tool_names_map.values())

    @cached_property
    def component_label_map(self) -> dict[str, list[str]]:
        """Map component ID → list of label texts from html.Label containers
        and/or `htmlFor` associations.
        """
        layout = get_app().get_layout()
        if layout is None:
            return {}

        labels: dict[str, list[str]] = {}
        for comp, ancestors in traverse(layout):
            if getattr(comp, "_type", None) == "Label":
                html_for = getattr(comp, "htmlFor", None)
                if html_for is not None:
                    text = extract_text(comp)
                    if text:
                        labels.setdefault(str(html_for), []).append(text)

            comp_id = getattr(comp, "id", None)
            if comp_id is not None:
                for ancestor in reversed(ancestors):
                    if getattr(ancestor, "_type", None) == "Label":
                        text = extract_text(ancestor)
                        if text:
                            sid = str(comp_id)
                            if text not in labels.get(sid, []):
                                labels.setdefault(sid, []).append(text)
                        break

        return labels
