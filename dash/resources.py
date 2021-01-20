import json
import warnings
import os

from .development.base_component import ComponentRegistry
from . import exceptions


class Resources:
    def __init__(self, resource_name):
        self._resources = []
        self.resource_name = resource_name

    def append_resource(self, resource):
        self._resources.append(resource)

    # pylint: disable=too-many-branches
    def _filter_resources(self, all_resources, dev_bundles=False):
        filtered_resources = []
        for s in all_resources:
            filtered_resource = {}
            if "dynamic" in s:
                filtered_resource["dynamic"] = s["dynamic"]
            if "async" in s:
                if "dynamic" in s:
                    raise exceptions.ResourceException(
                        """
                        Can't have both 'dynamic' and 'async'.
                        {}
                        """.format(
                            json.dumps(filtered_resource)
                        )
                    )

                # Async assigns a value dynamically to 'dynamic'
                # based on the value of 'async' and config.eager_loading
                #
                # True -> dynamic if the server is not eager, False otherwise
                # 'lazy' -> always dynamic
                # 'eager' -> dynamic if server is not eager
                # (to prevent ever loading it)
                filtered_resource["dynamic"] = (
                    not self.config.eager_loading
                    if s["async"] is True
                    else (s["async"] == "eager" and not self.config.eager_loading)
                    or s["async"] == "lazy"
                )
            if "namespace" in s:
                filtered_resource["namespace"] = s["namespace"]
            if "external_url" in s and not self.config.serve_locally:
                filtered_resource["external_url"] = s["external_url"]
            elif "dev_package_path" in s and dev_bundles:
                filtered_resource["relative_package_path"] = s["dev_package_path"]
            elif "relative_package_path" in s:
                filtered_resource["relative_package_path"] = s["relative_package_path"]
            elif "absolute_path" in s:
                filtered_resource["absolute_path"] = s["absolute_path"]
            elif "asset_path" in s:
                info = os.stat(s["filepath"])
                filtered_resource["asset_path"] = s["asset_path"]
                filtered_resource["ts"] = info.st_mtime
            elif self.config.serve_locally:
                warnings.warn(
                    (
                        "You have set your config to `serve_locally=True` but "
                        "A local version of {} is not available.\n"
                        "If you added this file with "
                        "`app.scripts.append_script` "
                        "or `app.css.append_css`, use `external_scripts` "
                        "or `external_stylesheets` instead.\n"
                        "See https://dash.plot.com/external-resources"
                    ).format(s["external_url"])
                )
                continue
            else:
                raise exceptions.ResourceException(
                    """
                    {} does not have a relative_package_path, absolute_path,
                    or an external_url.
                    """.format(
                        json.dumps(filtered_resource)
                    )
                )

            filtered_resources.append(filtered_resource)

        return filtered_resources

    def get_all_resources(self, dev_bundles=False):
        lib_resources = ComponentRegistry.get_resources(self.resource_name)
        all_resources = lib_resources + self._resources

        return self._filter_resources(all_resources, dev_bundles)


# pylint: disable=too-few-public-methods
class _Config:
    def __init__(self, serve_locally, eager_loading):
        self.eager_loading = eager_loading
        self.serve_locally = serve_locally


class Css:
    def __init__(self, serve_locally):
        self._resources = Resources("_css_dist")
        self._resources.config = self.config = _Config(serve_locally, True)

    def append_css(self, stylesheet):
        self._resources.append_resource(stylesheet)

    def get_all_css(self):
        return self._resources.get_all_resources()


class Scripts:
    def __init__(self, serve_locally, eager):
        self._resources = Resources("_js_dist")
        self._resources.config = self.config = _Config(serve_locally, eager)

    def append_script(self, script):
        self._resources.append_resource(script)

    def get_all_scripts(self, dev_bundles=False):
        return self._resources.get_all_resources(dev_bundles)
