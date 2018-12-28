import unittest
import mock
import dash_core_components as dcc

import dash

_monkey_patched_js_dist = [
    {
        'external_url': 'https://external_javascript.js',
        'relative_package_path': 'external_javascript.js',
        'namespace': 'dash_core_components'
    },
    {
        'external_url': 'https://external_css.css',
        'relative_package_path': 'external_css.css',
        'namespace': 'dash_core_components'
    },
    {
        'relative_package_path': 'fake_dcc.js',
        'dev_package_path': 'fake_dcc.dev.js',
        'external_url': 'https://component_library.bundle.js',
        'namespace': 'dash_core_components'
    },
    {
        'relative_package_path': 'fake_dcc.min.js.map',
        'dev_package_path': 'fake_dcc.dev.js.map',
        'external_url': 'https://component_library.bundle.js.map',
        'namespace': 'dash_core_components',
        'dynamic': True
    }
]

dcc._js_dist = _monkey_patched_js_dist
dcc.__version__ = 1


class StatMock(object):
    st_mtime = 1


class Tests(unittest.TestCase):

    def test_external(self):
        app = dash.Dash(
            __name__,
            assets_folder='tests/assets',
            assets_ignore='load_after.+.js'
        )
        app.layout = dcc.Markdown()
        app.scripts.config.serve_locally = False

        with mock.patch('dash.dash.os.stat', return_value=StatMock()):
            resource = app._collect_and_register_resources(
                app.scripts.get_all_scripts()
            )

        self.assertEqual(resource, [
            'https://external_javascript.js',
            'https://external_css.css',
            'https://component_library.bundle.js'
        ])

    def test_internal(self):
        app = dash.Dash(
            __name__,
            assets_folder='tests/assets',
            assets_ignore='load_after.+.js'
        )
        app.layout = dcc.Markdown()
        app.scripts.config.serve_locally = True

        with mock.patch('dash.dash.os.stat', return_value=StatMock()):
            with mock.patch('dash.dash.importlib.import_module',
                            return_value=dcc):
                resource = app._collect_and_register_resources(
                    app.scripts.get_all_scripts()
                )

        self.assertEqual(resource, [
            '/_dash-component-suites/'
            'dash_core_components/external_javascript.js?v=1&m=1',
            '/_dash-component-suites/'
            'dash_core_components/external_css.css?v=1&m=1',
            '/_dash-component-suites/'
            'dash_core_components/fake_dcc.js?v=1&m=1',
        ])

        self.assertTrue(
            'fake_dcc.min.js.map'
            in app.registered_paths['dash_core_components'],
            'Dynamic resource not available in registered path {}'.format(
                app.registered_paths['dash_core_components']
            )
        )
