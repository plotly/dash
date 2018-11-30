import unittest
import warnings
from dash.resources import Scripts, Css
from dash.development._py_components_generation import generate_class


def generate_components():
    Div = generate_class('Div', ('children', 'id',), 'dash_html_components')
    Span = generate_class('Span', ('children', 'id',), 'dash_html_components')
    Input = generate_class(
        'Input', ('children', 'id',),
        'dash_core_components')
    return Div, Span, Input


def external_url(package_name):
    return (
        '//unpkg.com/{}@0.2.9'
        '/{}/bundle.js'.format(
            package_name.replace('_', '-'),
            package_name
        )
    )


def rel_path(package_name):
    return '{}/bundle.js'.format(package_name)


def abs_path(package_name):
    return '/Users/chriddyp/{}/bundle.js'.format(package_name)


class TestResources(unittest.TestCase):

    def resource_test(self, css_or_js):
        Div, Span, Input = generate_components()

        if css_or_js == 'css':
            # The CSS URLs and paths will look a little bit differently
            # than the JS urls but that doesn't matter for the purposes
            # of the test
            Div._css_dist = Span._css_dist = [{
                'external_url': external_url('dash_html_components'),
                'relative_package_path': rel_path('dash_html_components')
            }]

            Input._css_dist = [{
                'external_url': external_url('dash_core_components'),
                'relative_package_path': rel_path('dash_core_components')
            }]

        else:
            Div._js_dist = Span._js_dist = [{
                'external_url': external_url('dash_html_components'),
                'relative_package_path': rel_path('dash_html_components')
            }]

            Input._js_dist = [{
                'external_url': external_url('dash_core_components'),
                'relative_package_path': rel_path('dash_core_components')
            }]

        layout = Div([None, 'string', Span(), Div(Input())])

        if css_or_js == 'css':
            resources = Css(layout)
        else:
            resources = Scripts(layout)

        resources._update_layout(layout)

        expected_filtered_external_resources = [
            {
                'external_url': external_url('dash_html_components'),
                'namespace': 'dash_html_components'
            },
            {
                'external_url': external_url('dash_core_components'),
                'namespace': 'dash_core_components'
            }
        ]
        expected_filtered_relative_resources = [
            {
                'relative_package_path': rel_path('dash_html_components'),
                'namespace': 'dash_html_components'
            },
            {
                'relative_package_path': rel_path('dash_core_components'),
                'namespace': 'dash_core_components'
            }
        ]

        if css_or_js == 'css':
            self.assertEqual(
                resources.get_all_css(),
                expected_filtered_external_resources
            )
        else:
            self.assertEqual(
                resources.get_all_scripts(),
                expected_filtered_external_resources
            )

        resources.config.serve_locally = True
        if css_or_js == 'css':
            self.assertEqual(
                resources.get_all_css(),
                expected_filtered_relative_resources
            )
        else:
            self.assertEqual(
                resources.get_all_scripts(),
                expected_filtered_relative_resources
            )

        resources.config.serve_locally = False
        extra_resource = {'external_url': '//cdn.bootstrap.com/min.css'}
        expected_resources = expected_filtered_external_resources + [
            extra_resource
        ]
        if css_or_js == 'css':
            resources.append_css(extra_resource)
            self.assertEqual(
                resources.get_all_css(),
                expected_resources
            )
        else:
            resources.append_script(extra_resource)
            self.assertEqual(
                resources.get_all_scripts(),
                expected_resources
            )

        resources.config.serve_locally = True
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            if css_or_js == 'css':
                self.assertEqual(
                    resources.get_all_css(),
                    expected_filtered_relative_resources
                )
                assert len(w) == 1
                assert 'A local version of {} is not available'.format(
                    extra_resource['external_url']
                ) in str(w[-1].message)

            else:
                self.assertEqual(
                    resources.get_all_scripts(),
                    expected_filtered_relative_resources
                )
                assert len(w) == 1
                assert 'A local version of {} is not available'.format(
                    extra_resource['external_url']
                ) in str(w[-1].message)

    def test_js_resources(self):
        # self.resource_test('js')
        pass

    def test_css_resources(self):
        # self.resource_test('css')
        pass
