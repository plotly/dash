"""Stub — real implementation in a later PR."""


def build_tool_description(outputs, docstring=None):  # pylint: disable=unused-argument
    if docstring:
        return docstring.strip()
    return "Dash callback"
