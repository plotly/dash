import mock
import dash
from dash import dcc, html  # noqa: F401

from dash.development.base_component import ComponentRegistry

_monkey_patched_js_dist = [
    {
        "external_url": "https://external_javascript.js",
        "relative_package_path": "external_javascript.js",
        "namespace": "dash",
    },
    {
        "external_url": "https://external_css.css",
        "relative_package_path": "external_css.css",
        "namespace": "dash",
    },
    {
        "relative_package_path": "fake_dcc.js",
        "dev_package_path": "fake_dcc.dev.js",
        "external_url": "https://component_library.bundle.js",
        "namespace": "dash",
    },
    {
        "relative_package_path": "fake_dcc.min.js.map",
        "dev_package_path": "fake_dcc.dev.js.map",
        "external_url": "https://component_library.bundle.js.map",
        "namespace": "dash",
        "dynamic": True,
    },
]


class StatMock(object):
    st_mtime = 1


def test_external(mocker):
    assert "dash" in ComponentRegistry.registry
    mocker.patch("dash.development.base_component.ComponentRegistry.registry")
    ComponentRegistry.registry = {"dash", "dash.dcc", "dash.html"}

    mocker.patch("dash.dcc._js_dist")
    mocker.patch("dash.dcc.__version__")
    mocker.patch("dash.html._js_dist")
    dcc._js_dist = _monkey_patched_js_dist  # noqa: W0212
    dcc.__version__ = "1.0.0"

    app = dash.Dash(
        __name__, assets_folder="tests/assets", assets_ignore="load_after.+.js"
    )
    app.layout = dcc.Markdown()
    app.scripts.config.serve_locally = False

    resource = app._collect_and_register_resources(app.scripts.get_all_scripts())

    assert resource == [
        "https://external_javascript.js",
        "https://external_css.css",
        "https://component_library.bundle.js",
    ]


def test_external_kwarg():
    app = dash.Dash(__name__, serve_locally=False)
    assert not app.scripts.config.serve_locally
    assert not app.css.config.serve_locally


def test_internal(mocker):
    assert "dash" in ComponentRegistry.registry
    mocker.patch("dash.development.base_component.ComponentRegistry.registry")
    ComponentRegistry.registry = {"dash", "dash.dcc", "dash.html"}

    mocker.patch("dash.dcc._js_dist")
    mocker.patch("dash.dcc.__version__")
    mocker.patch("dash.html._js_dist")
    dcc._js_dist = _monkey_patched_js_dist  # noqa: W0212,
    dcc.__version__ = "1.0.0"

    app = dash.Dash(
        __name__, assets_folder="tests/assets", assets_ignore="load_after.+.js"
    )
    app.layout = dcc.Markdown()

    assert app.scripts.config.serve_locally and app.css.config.serve_locally

    with mock.patch("dash.dash.os.stat", return_value=StatMock()):
        with mock.patch("dash.dash.importlib.import_module", return_value=dcc):
            resource = app._collect_and_register_resources(
                app.scripts.get_all_scripts()
            )

    assert resource == [
        "/_dash-component-suites/" "dash/external_javascript.v1_0_0m1.js",
        "/_dash-component-suites/dash/external_css.v1_0_0m1.css",
        "/_dash-component-suites/dash/fake_dcc.v1_0_0m1.js",
    ]

    assert (
        "fake_dcc.min.js.map" in app.registered_paths["dash"]
    ), "Dynamic resource not available in registered path {}".format(
        app.registered_paths["dash"]
    )


def test_collect_and_register_resources(mocker):

    app = dash.Dash(
        __name__, assets_folder="tests/assets", assets_ignore="load_after.+.js"
    )
    with mock.patch("dash.dash.os.stat", return_value=StatMock()):
        with mock.patch("dash.dash.importlib.import_module") as import_mock:
            with mock.patch("sys.modules", {"dash_html_components": dcc}):
                import_mock.return_value = dcc
                app._collect_and_register_resources(
                    [
                        {
                            "namespace": "dash_html_components",
                            "relative_package_path": "dash_html_components.min.js",
                        },
                    ]
                )
                import_mock.assert_any_call("dash_html_components")
