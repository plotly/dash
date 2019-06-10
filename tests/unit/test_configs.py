import os
import unittest
# noinspection PyProtectedMember
from dash._configs import (
    pathname_configs, DASH_ENV_VARS, get_combined_config, load_dash_env_vars)
from dash import exceptions as _exc
from dash._utils import get_asset_path


class TestConfigs(unittest.TestCase):

    def setUp(self):
        for k in DASH_ENV_VARS.keys():
            if k in os.environ:
                os.environ.pop(k)

    def test_dash_env_vars(self):
        self.assertEqual(
            {None}, {val for _, val in DASH_ENV_VARS.items()},
            "initial var values are None without extra OS environ setting")

    def test_valid_pathname_prefix_init(self):
        _, routes, req = pathname_configs()

        self.assertEqual('/', routes)
        self.assertEqual('/', req)

        _, routes, req = pathname_configs(
            routes_pathname_prefix='/dash/')

        self.assertEqual('/dash/', req)

        _, routes, req = pathname_configs(
            requests_pathname_prefix='/my-dash-app/',
        )

        self.assertEqual(routes, '/')
        self.assertEqual(req, '/my-dash-app/')

        _, routes, req = pathname_configs(
            routes_pathname_prefix='/dash/',
            requests_pathname_prefix='/my-dash-app/dash/'
        )

        self.assertEqual('/dash/', routes)
        self.assertEqual('/my-dash-app/dash/', req)

    def test_invalid_pathname_prefix(self):
        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = pathname_configs('/my-path', '/another-path')

            self.assertTrue('url_base_pathname' in str(context.exception))

        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = pathname_configs(
                url_base_pathname='/invalid',
                routes_pathname_prefix='/invalid')

            self.assertTrue(str(context.exception).split('.')[0]
                            .endswith('`routes_pathname_prefix`'))

        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = pathname_configs(
                url_base_pathname='/my-path',
                requests_pathname_prefix='/another-path')

            self.assertTrue(str(context.exception).split('.')[0]
                            .endswith('`requests_pathname_prefix`'))

        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = pathname_configs('my-path')

            self.assertTrue('start with `/`' in str(context.exception))

        with self.assertRaises(_exc.InvalidConfig) as context:
            _, _, _ = pathname_configs('/my-path')

            self.assertTrue('end with `/`' in str(context.exception))

    def test_pathname_prefix_from_environ_app_name(self):
        os.environ['DASH_APP_NAME'] = 'my-dash-app'
        _, routes, req = pathname_configs()
        self.assertEqual('/my-dash-app/', req)
        self.assertEqual('/', routes)

    def test_pathname_prefix_environ_routes(self):
        os.environ['DASH_ROUTES_PATHNAME_PREFIX'] = '/routes/'
        _, routes, _ = pathname_configs()
        self.assertEqual('/routes/', routes)

    def test_pathname_prefix_environ_requests(self):
        os.environ['DASH_REQUESTS_PATHNAME_PREFIX'] = '/requests/'
        _, _, req = pathname_configs()
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

    def test_get_combined_config_dev_tools_ui(self):
        val1 = get_combined_config('ui', None, default=False)
        self.assertEqual(
            val1, False,
            "should return the default value if None is provided for init and environment")
        os.environ['DASH_UI'] = 'true'
        val2 = get_combined_config('ui', None, default=False)
        self.assertEqual(val2, True, "should return the set environment value as True")
        val3 = get_combined_config('ui', False, default=True)
        self.assertEqual(val3, False, "init value overrides the environment value")

    def test_get_combined_config_props_check(self):
        val1 = get_combined_config('props_check', None, default=False)
        self.assertEqual(
            val1, False,
            "should return the default value if None is provided for init and environment")
        os.environ['DASH_PROPS_CHECK'] = 'true'
        val2 = get_combined_config('props_check', None, default=False)
        self.assertEqual(val2, True, "should return the set environment value as True")
        val3 = get_combined_config('props_check', False, default=True)
        self.assertEqual(val3, False, "init value overrides the environment value")

    def test_load_dash_env_vars_refects_to_os_environ(self):
        for var in DASH_ENV_VARS.keys():
            os.environ[var] = 'true'
            vars = load_dash_env_vars()
            self.assertEqual(vars[var], 'true')
            os.environ[var] = 'false'
            vars = load_dash_env_vars()
            self.assertEqual(vars[var], 'false')


if __name__ == '__main__':
    unittest.main()
