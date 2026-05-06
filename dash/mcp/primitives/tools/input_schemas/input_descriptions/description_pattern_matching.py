"""Description for pattern-matching callback inputs.

Explains that the input corresponds to a pattern-matching callback
(ALL, MATCH, ALLSMALLER) and describes the expected format.
See: https://dash.plotly.com/pattern-matching-callbacks
"""

from __future__ import annotations

from dash._layout_utils import _WILDCARD_VALUES, parse_wildcard_id
from dash.mcp.types import MCPInput

from .base import InputDescriptionSource


class PatternMatchingDescription(InputDescriptionSource):
    """Describe pattern-matching behavior for wildcard inputs."""

    @classmethod
    def describe(cls, param: MCPInput) -> list[str]:
        dep_id = parse_wildcard_id(param["component_id"])
        if dep_id is None:
            return []

        wildcard_key, wildcard_type = _find_wildcard(dep_id)
        if wildcard_key is None:
            return []

        non_wildcard = {k: v for k, v in dep_id.items() if k != wildcard_key}
        pattern_desc = ", ".join(f'{k}="{v}"' for k, v in non_wildcard.items())
        prop = param["property"]

        wildcard_descriptions = {
            "ALL": (
                f"Pattern-matching input (ALL): provide an array of `{prop}` values, "
                f"one per component matching {{{pattern_desc}}}. "
                f"All matching components are included."
            ),
            "MATCH": (
                f"Pattern-matching input (MATCH): provide the `{prop}` value "
                f"for the specific component matching {{{pattern_desc}}} "
                f"that triggered this callback."
            ),
            "ALLSMALLER": (
                f"Pattern-matching input (ALLSMALLER): provide an array of `{prop}` values "
                f"from components matching {{{pattern_desc}}} "
                f"whose `{wildcard_key}` is smaller than the triggering component's `{wildcard_key}`."
            ),
        }

        desc = wildcard_descriptions.get(wildcard_type)
        return [desc] if desc else []


def _find_wildcard(dep_id: dict) -> tuple[str | None, str | None]:
    """Return (key, wildcard_type) for the first wildcard found."""
    for key, value in dep_id.items():
        if isinstance(value, list) and len(value) == 1:
            if value[0] in _WILDCARD_VALUES:
                return key, value[0]
    return None, None
