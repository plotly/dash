"""Adapter: Dash callback → MCP tool interface.

Wraps a raw ``callback_map`` entry and exposes MCP-facing
properties (tool name, params, outputs) lazily.
"""

from __future__ import annotations

import inspect
import json
import typing
from functools import cached_property
from typing import Any, cast

from mcp.types import Tool

from dash import get_app
from dash._layout_utils import (
    _WILDCARD_VALUES,
    find_component,
    find_matching_components,
    parse_wildcard_id,
)
from dash._grouping import flatten_grouping
from dash._utils import clean_property_name, split_callback_id
from dash.types import (
    CallbackDependency,
    CallbackExecutionBody,
    CallbackInput,
    CallbackInputs,
    CallbackOutput,
    CallbackOutputTarget,
    WildcardId,
)
from dash.mcp.types import MCPInput, MCPOutput, is_nullable
from .callback_utils import run_callback
from .descriptions import build_tool_description
from .input_schemas import get_input_schema
from .output_schemas import get_output_schema


class CallbackAdapter:
    """Adapts a single Dash callback_map entry to the MCP tool interface."""

    def __init__(self, callback_output_id: str):
        self._output_id = callback_output_id

    # -------------------------------------------------------------------
    # Projections
    # -------------------------------------------------------------------

    @cached_property
    def as_mcp_tool(self) -> Tool:
        """Transforms the internal Dash callback to a structured MCP tool.

        This tool can be serialized for LLM consumption or used internally for
        its computed data.
        """
        return Tool(
            name=self.tool_name,
            description=self._description,
            inputSchema=self._input_schema,
            outputSchema=self._output_schema,
        )

    def as_callback_body(self, kwargs: dict[str, Any]) -> CallbackExecutionBody:
        """Transforms the given kwargs to a dict suitable for calling this callback.

        Mirrors how the Dash renderer assembles the callback payload —
        see ``fillVals()`` in ``dash-renderer/src/actions/callbacks.ts``.

        For pattern-matching callbacks, wildcard deps are expanded into
        nested arrays with concrete component IDs.
        """
        raw_inputs = self._cb_info.get("inputs", [])
        raw_state = self._cb_info.get("state", [])
        n_deps = len(raw_inputs) + len(raw_state)

        flat_values = [None] * n_deps
        for i, name in enumerate(self._param_names):
            if i < n_deps and name in kwargs:
                flat_values[i] = kwargs[name]

        inputs_with_values = [
            _expand_dep(dep, flat_values[i]) for i, dep in enumerate(raw_inputs)
        ]
        state_with_values = [
            _expand_dep(dep, flat_values[len(raw_inputs) + i])
            for i, dep in enumerate(raw_state)
        ]

        outputs_spec = _expand_output_spec(
            self._output_id, self._cb_info, inputs_with_values
        )

        # changedPropIds: only inputs with non-None values.
        # This determines ctx.triggered_id in the callback.
        changed = []
        for entry in inputs_with_values:
            if isinstance(entry, dict) and entry.get("value") is not None:
                eid = entry.get("id")
                if isinstance(eid, dict):
                    changed.append(
                        f"{json.dumps(eid, sort_keys=True)}.{entry['property']}"
                    )
                elif isinstance(eid, str):
                    changed.append(f"{eid}.{entry['property']}")

        return {
            "output": self._output_id,
            "outputs": outputs_spec,
            "inputs": inputs_with_values,
            "state": state_with_values,
            "changedPropIds": changed,
        }

    # -------------------------------------------------------------------
    # Public identity and metadata
    # -------------------------------------------------------------------

    @cached_property
    def is_valid(self) -> bool:
        """Whether all input components exist in the layout."""
        all_deps = self._cb_info.get("inputs", []) + self._cb_info.get("state", [])
        for dep in all_deps:
            dep_id = str(dep.get("id", ""))
            if dep_id.startswith("{"):
                continue
            if find_component(dep_id) is None:
                return False
        return True

    @property
    def output_id(self) -> str:
        return self._output_id

    @property
    def tool_name(self) -> str:
        # pylint: disable-next=protected-access
        return get_app().mcp_callback_map._tool_names_map[self._output_id]

    @cached_property
    def prevents_initial_call(self) -> bool:
        for cb in get_app()._callback_list:  # pylint: disable=protected-access
            if cb["output"] == self._output_id:
                return cb.get("prevent_initial_call", False)
        return False

    # -------------------------------------------------------------------
    # Private: computed fields for the MCP Tool
    # -------------------------------------------------------------------

    @cached_property
    def _description(self) -> str:
        return build_tool_description(self)

    @cached_property
    def _input_schema(self) -> dict[str, Any]:
        properties = {p["name"]: get_input_schema(p) for p in self.inputs}
        required = [p["name"] for p in self.inputs if p["required"]]

        input_schema: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            input_schema["required"] = required
        return input_schema

    @cached_property
    def _output_schema(self) -> dict[str, Any]:
        return get_output_schema()

    # -------------------------------------------------------------------
    # Private: callback metadata
    # -------------------------------------------------------------------

    @cached_property
    def _docstring(self) -> str | None:
        return getattr(self._original_func, "__doc__", None)

    @cached_property
    def _initial_output(self) -> dict[str, CallbackOutput]:
        """Run this callback with initial input values.

        Returns the ``response`` portion of the callback result:
        ``{component_id: {property: value}}``.

        Skipped for callbacks with ``prevent_initial_call=True``,
        matching how the Dash renderer skips them on page load.
        """
        if self.prevents_initial_call:
            return {}

        callback_map = get_app().mcp_callback_map
        kwargs = {}
        for p in self.inputs:
            upstream = callback_map.find_by_output(p["id_and_prop"])
            if upstream is self:
                kwargs[p["name"]] = getattr(
                    find_component(p["component_id"]), p["property"], None
                )
            else:
                kwargs[p["name"]] = callback_map.get_initial_value(p["id_and_prop"])
        try:
            result = run_callback(self, kwargs)
            return result.get("response", {})
        except Exception:  # pylint: disable=broad-exception-caught
            return {}

    def initial_output_value(self, id_and_prop: str) -> Any:
        """Return the initial value for a specific output ``"component_id.property"``."""
        component_id, prop = id_and_prop.rsplit(".", 1)
        return self._initial_output.get(component_id, {}).get(prop)

    @cached_property
    def outputs(self) -> list[MCPOutput]:
        if self._cb_info.get("no_output"):
            return []
        parsed = split_callback_id(self._output_id)
        if isinstance(parsed, dict):
            parsed = [parsed]
        result: list[MCPOutput] = []
        for p in parsed:
            comp_id = p["id"]
            prop = clean_property_name(p["property"])
            id_and_prop = f"{comp_id}.{prop}"
            comp = find_component(comp_id)
            result.append(
                {
                    "id_and_prop": id_and_prop,
                    "component_id": comp_id,
                    "property": prop,
                    "component_type": getattr(comp, "_type", None),
                    "initial_value": self.initial_output_value(id_and_prop),
                    "tool_name": self.tool_name,
                }
            )
        return result

    @cached_property
    def inputs(self) -> list[MCPInput]:
        all_deps = self._cb_info.get("inputs", []) + self._cb_info.get("state", [])
        callback_map = get_app().mcp_callback_map

        result: list[MCPInput] = []
        for dep, name, annotation in zip(
            all_deps, self._param_names, self._param_annotations
        ):
            comp_id = str(dep.get("id", "unknown"))
            comp = find_component(comp_id)
            prop = dep.get("property", "unknown")
            id_and_prop = f"{comp_id}.{prop}"

            upstream_cb = callback_map.find_by_output(id_and_prop)
            upstream_output = None
            if upstream_cb is not None and upstream_cb is not self:
                if not upstream_cb.prevents_initial_call:
                    for out in upstream_cb.outputs:
                        if out["id_and_prop"] == id_and_prop:
                            upstream_output = out
                            break

            initial_value = (
                upstream_output["initial_value"]
                if upstream_output is not None
                else getattr(comp, prop, None)
            )

            if annotation is not None:
                required = not is_nullable(annotation)
            else:
                required = initial_value is not None

            result.append(
                {
                    "name": name,
                    "id_and_prop": id_and_prop,
                    "component_id": comp_id,
                    "property": prop,
                    "annotation": annotation,
                    "component_type": getattr(comp, "_type", None),
                    "component": comp,
                    "required": required,
                    "initial_value": initial_value,
                    "upstream_output": upstream_output,
                }
            )
        return result

    # -------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------

    @cached_property
    def _cb_info(self) -> dict[str, Any]:
        return get_app().callback_map[self._output_id]

    @cached_property
    def _original_func(self) -> Any | None:
        func = self._cb_info.get("callback")
        return getattr(func, "__wrapped__", func)

    @cached_property
    def _func_signature(self) -> inspect.Signature | None:
        if self._original_func is None:
            return None
        try:
            return inspect.signature(self._original_func)
        except (ValueError, TypeError):
            return None

    @cached_property
    def _dep_param_map(self) -> list[tuple[str, str]]:
        """(func_param_name, mcp_param_name) per dep, in dep order.

        Single source of truth for mapping deps to param names.
        All dict-vs-list branching is confined here.
        """
        all_deps = self._cb_info.get("inputs", []) + self._cb_info.get("state", [])
        n_deps = len(all_deps)
        indices = self._cb_info.get("inputs_state_indices")

        if isinstance(indices, dict):
            entries: list[tuple[int, str, str]] = []
            for func_name, idx in indices.items():
                positions = flatten_grouping(idx)
                if len(positions) == 1:
                    entries.append((positions[0], func_name, func_name))
                else:
                    for pos in positions:
                        dep = all_deps[pos] if pos < n_deps else {}
                        comp_id = str(dep.get("id", "unknown")).replace("-", "_")
                        prop = dep.get("property", "unknown")
                        entries.append(
                            (pos, func_name, f"{func_name}_{comp_id}__{prop}")
                        )
            entries.sort(key=lambda e: e[0])
            result = [(f, m) for _, f, m in entries]
        elif self._func_signature is not None:
            names = list(self._func_signature.parameters.keys())
            result = [(n, n) for n in names]
        else:
            result = []

        while len(result) < n_deps:
            fallback = f"param_{len(result)}"
            result.append((fallback, fallback))
        return result

    @cached_property
    def _param_names(self) -> list[str]:
        """MCP param name per dep, in dep order."""
        return [mcp for _, mcp in self._dep_param_map]

    @cached_property
    def _param_annotations(self) -> list[Any | None]:
        """One annotation per dep, in dep order."""
        if self._func_signature is None:
            return [None] * len(self._dep_param_map)
        try:
            hints = typing.get_type_hints(self._original_func)
        except Exception:  # pylint: disable=broad-exception-caught
            hints = getattr(self._original_func, "__annotations__", {})
        return [hints.get(func_name) for func_name, _ in self._dep_param_map]


def _expand_dep(dep: CallbackDependency, value: Any) -> CallbackInputs:
    """
    Attach a concrete value to a callback dependency to produce a valid callback input.

    For regular deps, returns ``{id, property, value}``.
    For ALL/ALLSMALLER: passes through the list of ``{id, property, value}`` dicts.
    For MATCH: passes through the single ``{id, property, value}`` dict.
    """
    pattern = parse_wildcard_id(dep.get("id", ""))
    if pattern is None:
        return CallbackInput(id=dep["id"], property=dep["property"], value=value)

    # LLM provides browser-like format
    if isinstance(value, list):
        return cast("list[CallbackInput]", value)
    if isinstance(value, dict) and "id" in value:
        return cast(CallbackInput, value)
    return CallbackInput(id=dep["id"], property=dep["property"], value=value)


def _expand_output_spec(
    output_id: str,
    cb_info: dict,
    resolved_inputs: list[CallbackInputs],
) -> CallbackOutputTarget | list[CallbackOutputTarget]:
    """Build the outputs spec, expanding wildcards to concrete IDs.

    For wildcard outputs, derives concrete IDs from the resolved inputs.
    The browser does the same: input and output wildcards resolve against
    the same set of matching components.
    """
    if cb_info.get("no_output"):
        return []

    parsed = split_callback_id(output_id)
    if isinstance(parsed, dict):
        parsed = [parsed]

    results: list[CallbackOutputTarget] = []
    for p in parsed:
        pid = p["id"]
        prop = clean_property_name(p["property"])
        pattern = parse_wildcard_id(pid)
        if pattern is not None:
            concrete_ids = _derive_output_ids(pattern, resolved_inputs)
            if not concrete_ids:
                concrete_ids = [
                    getattr(comp, "id") for comp in find_matching_components(pattern)
                ]
            expanded: list[CallbackDependency] = [
                CallbackDependency(id=cid, property=prop) for cid in concrete_ids
            ]
            # ALL/ALLSMALLER → nested list; MATCH → single dict
            if len(expanded) == 1:
                results.append(expanded[0])
            else:
                results.append(expanded)
        else:
            results.append(CallbackDependency(id=pid, property=prop))

    # Mirror the Dash renderer: single-output callbacks send a bare dict,
    # multi-output callbacks send a list. The framework's output value
    # matching depends on this shape.
    if len(results) == 1:
        return results[0]
    return results


def _derive_output_ids(
    output_pattern: WildcardId,
    resolved_inputs: list[CallbackInputs],
) -> list[WildcardId] | None:
    """Derive concrete output IDs from the resolved input entries.

    Extracts the wildcard key values from the LLM-provided concrete
    input IDs and substitutes them into the output pattern.
    """
    wildcard_keys = [
        k
        for k, v in output_pattern.items()
        if isinstance(v, list) and len(v) == 1 and v[0] in _WILDCARD_VALUES
    ]
    if not wildcard_keys:
        return None

    def _substitute(item_id: WildcardId) -> WildcardId | None:
        if not isinstance(item_id, dict):
            return None
        output_id = dict(output_pattern)
        for wk in wildcard_keys:
            if wk in item_id:
                output_id[wk] = item_id[wk]
        return output_id

    for entry in resolved_inputs:
        # ALL/ALLSMALLER: nested array of {id, property, value} dicts
        if isinstance(entry, list) and entry:
            concrete_ids = []
            for item in entry:
                item_id = item.get("id")
                if isinstance(item_id, dict):
                    out = _substitute(item_id)
                    if out:
                        concrete_ids.append(out)
            if concrete_ids:
                return concrete_ids
        # MATCH: single {id, property, value} dict
        elif isinstance(entry, dict):
            entry_id = entry.get("id")
            if isinstance(entry_id, dict):
                out = _substitute(entry_id)
                if out:
                    return [out]

    return None
