"""Unit tests for partial pattern matching in dependencies."""
from dash.dependencies import Input, Output, State, MATCH, ALL


class TestPartialIdMatches:
    """Test _id_matches with partial=True."""

    def test_partial_subset_keys_match(self):
        """Pattern with fewer keys should match component with more keys."""
        pattern = Input({"type": "btn"}, "n_clicks", partial=True)
        component = Input({"type": "btn", "index": 1}, "n_clicks")
        assert pattern == component

    def test_partial_subset_keys_no_match_value(self):
        """Pattern with a literal value that doesn't match should fail."""
        pattern = Input({"type": "btn"}, "n_clicks", partial=True)
        component = Input({"type": "link", "index": 1}, "n_clicks")
        assert pattern != component

    def test_partial_wildcard_match(self):
        """Partial pattern with MATCH wildcard should match any type value."""
        pattern = Input({"type": MATCH}, "n_clicks", partial=True)
        component = Input({"type": "btn", "index": 1}, "n_clicks")
        assert pattern == component

    def test_partial_all_wildcard(self):
        """Partial pattern with ALL wildcard should match."""
        pattern = Input({"type": ALL}, "n_clicks", partial=True)
        component = Input({"type": "btn", "index": 1, "page": "home"}, "n_clicks")
        assert pattern == component

    def test_partial_no_common_keys(self):
        """Pattern with no common keys should not match."""
        pattern = Input({"category": "nav"}, "n_clicks", partial=True)
        component = Input({"type": "btn", "index": 1}, "n_clicks")
        assert pattern != component

    def test_partial_exact_same_keys(self):
        """Partial with exact same keys should still work like normal."""
        pattern = Input({"type": MATCH, "index": 1}, "n_clicks", partial=True)
        component = Input({"type": "btn", "index": 1}, "n_clicks")
        assert pattern == component

    def test_non_partial_different_keys_no_match(self):
        """Without partial, different keys should not match (existing behavior)."""
        pattern = Input({"type": "btn"}, "n_clicks")
        component = Input({"type": "btn", "index": 1}, "n_clicks")
        assert pattern != component

    def test_partial_multiple_pattern_keys(self):
        """Partial with multiple keys, component has even more."""
        pattern = Input({"type": "btn", "page": "home"}, "n_clicks", partial=True)
        component = Input(
            {"type": "btn", "page": "home", "index": 1, "section": "main"},
            "n_clicks",
        )
        assert pattern == component

    def test_partial_multiple_pattern_keys_one_mismatch(self):
        """Partial with multiple keys where one doesn't match."""
        pattern = Input({"type": "btn", "page": "home"}, "n_clicks", partial=True)
        component = Input(
            {"type": "btn", "page": "settings", "index": 1},
            "n_clicks",
        )
        assert pattern != component

    def test_partial_output(self):
        """Output with partial=True should work."""
        pattern = Output({"type": "display"}, "children", partial=True)
        component = Output({"type": "display", "index": 1}, "children")
        assert pattern == component

    def test_partial_state(self):
        """State with partial=True should work."""
        pattern = State({"type": "store"}, "data", partial=True)
        component = State({"type": "store", "page": "main"}, "data")
        assert pattern == component

    def test_partial_different_property_no_match(self):
        """Even with partial, different properties should not match."""
        pattern = Input({"type": "btn"}, "n_clicks", partial=True)
        component = Input({"type": "btn", "index": 1}, "value")
        assert pattern != component

    def test_partial_to_dict_includes_flag(self):
        """to_dict() should include partial: True."""
        dep = Input({"type": MATCH}, "n_clicks", partial=True)
        d = dep.to_dict()
        assert d["partial"] is True

    def test_non_partial_to_dict_excludes_flag(self):
        """to_dict() should not include partial when False."""
        dep = Input({"type": MATCH}, "n_clicks")
        d = dep.to_dict()
        assert "partial" not in d


class TestPartialMatchSymmetry:
    """Test that partial matching is directional - the partial-flagged dep
    is the one that allows subset matching."""

    def test_other_side_partial(self):
        """If the 'other' side has partial=True, subset matching works."""
        pattern = Input({"type": "btn", "index": 1}, "n_clicks")
        component = Input({"type": "btn"}, "n_clicks", partial=True)
        # Either side having partial should enable subset matching
        assert pattern == component

    def test_component_superset_of_pattern(self):
        """Component has more keys than pattern - should match with partial."""
        pattern = Input({"type": MATCH}, "value", partial=True)
        component = Input({"type": "input", "index": 5, "tab": "first"}, "value")
        assert pattern == component
