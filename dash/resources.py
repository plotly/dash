from copy import copy
import warnings
import collections

from .development.base_component import Component


class Resources():
    def __init__(self, resource_name, layout):
        self._resources = []
        self.resource_name = resource_name
        self.layout = layout

    def append_resource(self, resource):
        self._resources.append(resource)

    def _filter_resources(self, all_resources):
        filtered_resources = []
        for s in all_resources:
            filtered_resource = {}
            if 'namespace' in s:
                filtered_resource['namespace'] = s['namespace']

            if 'external_url' in s and not self.config.serve_locally:
                filtered_resource['external_url'] = s['external_url']
            elif 'relative_package_path' in s:
                filtered_resource['relative_package_path'] = (
                    s['relative_package_path']
                )
            elif 'absolute_path' in s:
                filtered_resource['absolute_path'] = s['absolute_path']
            elif self.config.serve_locally:
                warnings.warn(
                    'A local version of {} is not available'.format(
                        s['external_url']
                    )
                )
                continue
            else:
                raise Exception(
                    '{} does not have a '
                    'relative_package_path, absolute_path, or an '
                    'external_url.'.format(
                        json.dumps(filtered_resource)
                    )
                )

            filtered_resources.append(filtered_resource)

        return filtered_resources

    def get_all_resources(self):
        all_resources = []
        if self.config.infer_from_layout:
            all_resources = (
                self.get_inferred_resources() + self._resources
            )
        else:
            all_resources = self._resources

        return self._filter_resources(all_resources)

    def get_inferred_resources(self):
        namespaces = []
        resources = []
        if isinstance(self.layout, collections.Callable):
            layout = self.layout()
        else:
            layout = self.layout

        def extract_resource_from_component(component):
            if (isinstance(component, Component) and
                    component._namespace not in namespaces):

                namespaces.append(component._namespace)

                if hasattr(component, self.resource_name):

                    component_resources = copy(
                        getattr(component, self.resource_name)
                    )
                    for r in component_resources:
                        r['namespace'] = component._namespace
                    resources.extend(component_resources)

        extract_resource_from_component(layout)
        for t in layout.traverse():
            extract_resource_from_component(t)
        return resources


class Css():
    def __init__(self, layout=None):
        self._resources = Resources('_css_dist', layout)
        self._resources.config = self.config

    def _update_layout(self, layout):
        self._resources.layout = layout

    def append_css(self, stylesheet):
        self._resources.append_resource(stylesheet)

    def get_all_css(self):
        return self._resources.get_all_resources()

    def get_inferred_css_dist(self):
        return self._resources.get_inferred_resources()

    class config:
        infer_from_layout = True
        serve_locally = False


class Scripts():
    def __init__(self, layout=None):
        self._resources = Resources('_js_dist', layout)
        self._resources.config = self.config

    def _update_layout(self, layout):
        self._resources.layout = layout

    def append_script(self, script):
        self._resources.append_resource(script)

    def get_all_scripts(self):
        return self._resources.get_all_resources()

    def get_inferred_scripts(self):
        return self._resources.get_inferred_resources()

    class config:
        infer_from_layout = True
        serve_locally = False
