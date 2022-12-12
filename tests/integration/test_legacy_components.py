from dash import Dash
from dash.development.base_component import Component, _explicitize_args


try:
    # Import to load into registry.
    import dash_generator_test_component_standard  # noqa: F401
except ImportError:
    pass


class PreCAPLegacyComponent(Component):
    """A MyStandardComponent component.
    MyComponent description

    Keyword arguments:

    - id (string; optional):
        The id of the component.

    - style (optional):
        The style.

    - value (string; default ''):
        The value to display.

    Note: due to the large number of props for this component,
    not all of them appear in the constructor signature, but
    they may still be used as keyword arguments."""

    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, style=Component.UNDEFINED, **kwargs):
        self._prop_names = ["id", "style", "value"]
        self._type = "MyStandardComponent"
        self._namespace = "dash_generator_test_component_standard"
        self._valid_wildcard_attributes = []
        self.available_properties = ["id", "style", "value"]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in []:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(PreCAPLegacyComponent, self).__init__(**args)


def test_leg001_legacy_pre_component_as_props(dash_duo):
    app = Dash(__name__)

    app.layout = PreCAPLegacyComponent(id="pre-cap", value="legacy")

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#pre-cap", "legacy")
    assert dash_duo.get_logs() == []
