import os
import unittest
# noinspection PyProtectedMember
from dash import _configs
from dash import exceptions as _exc
from dash._utils import get_asset_path


class MyTestCase(unittest.TestCase):

    def setUp(self):
        environ = _configs.env_configs()

        for k in environ.keys():
            if k in os.environ:
                os.environ.pop(k)

    def test_valid_pathname_prefix_init(self):
        _, routes, req = _configs.pathname_configs()

        self.assertEqual('/', routes)
        self.assertEqual('/', req)

        _, routes, req = _configs.pathname_configs(
            routes_pathname_prefix='/dash/')

        self.assertEqual('/dash/', req)

        _, routes, req = _configs.pathname_configs(
            requests_pathname_prefix='/my-dash-app/',
        )

        self.assertEqual(routes, '/')
        self.assertEqual(req, '/my-dash-app/')

        _, routes, req = _configs.pathname_configs(
            routes_pathname_prefix='/dash/',
            requests_pathname_prefix='/my-dash-app/dash/'
        )

        self.assertEqual('/dash/', routes)
        self.assertEqual('/my-dash-app/dash/', req)

    def test_invalid_pathname_prefix(self):
        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = _configs.pathname_configs('/my-path', '/another-path')

            self.assertTrue('url_base_pathname' in str(context.exception))

        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = _configs.pathname_configs(
                url_base_pathname='/invalid',
                routes_pathname_prefix='/invalid')

            self.assertTrue(str(context.exception).split('.')[0]
                            .endswith('`routes_pathname_prefix`'))

        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = _configs.pathname_configs(
                url_base_pathname='/my-path',
                requests_pathname_prefix='/another-path')

            self.assertTrue(str(context.exception).split('.')[0]
                            .endswith('`requests_pathname_prefix`'))

        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = _configs.pathname_configs('my-path')

            self.assertTrue('start with `/`' in str(context.exception))

        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = _configs.pathname_configs('/my-path')

            self.assertTrue('end with `/`' in str(context.exception))

    def test_pathname_prefix_from_environ_app_name(self):
        os.environ['DASH_APP_NAME'] = 'my-dash-app'
        _, routes, req = _configs.pathname_configs()
        self.assertEqual('/my-dash-app/', req)
        self.assertEqual('/', routes)

    def test_pathname_prefix_environ_routes(self):
        os.environ['DASH_ROUTES_PATHNAME_PREFIX'] = '/routes/'
        _, routes, req = _configs.pathname_configs()
        self.assertEqual('/routes/', routes)

    def test_pathname_prefix_environ_requests(self):
        os.environ['DASH_REQUESTS_PATHNAME_PREFIX'] = '/requests/'
        _, routes, req = _configs.pathname_configs()
        self.assertEqual('/requests/', req)

    def test_pathname_prefix_assets(self):
        req = '/'
        path = get_asset_path(req, 'reset.css', 'assets')
        self.assertEqual('/assets/reset.css', path)

        req = '/requests/'
        path = get_asset_path(req, 'reset.css', 'assets')
        self.assertEqual('/requests/assets/reset.css', path)

        req = '/requests/routes/'
        path = get_asset_path(req, 'reset.css', 'assets')
        self.assertEqual('/requests/routes/assets/reset.css', path)


if __name__ == '__main__':
    unittest.main()
