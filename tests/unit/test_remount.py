import pytest

from dash import remount, html


def test_remount_adds_top_level_marker_not_a_prop():
    component = remount(html.Div("hello", id="d"))
    as_json = component.to_plotly_json()

    # Marker is a top-level key, a sibling of props/type/namespace...
    assert as_json["_dashprivate_remount"] is True
    # ...and never leaks into the component's props.
    assert "_dashprivate_remount" not in as_json["props"]


def test_remount_returns_same_component():
    div = html.Div(id="d")
    assert remount(div) is div


def test_plain_component_has_no_marker():
    assert "_dashprivate_remount" not in html.Div(id="d").to_plotly_json()


def test_remount_rejects_non_components():
    with pytest.raises(TypeError):
        remount("not a component")
    with pytest.raises(TypeError):
        remount({"type": "Div"})
