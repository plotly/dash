import json
import warnings
import os

import typing as _t
import typing_extensions as _tx


from .development.base_component import ComponentRegistry
from . import exceptions


# ResourceType has `async` key, use the init form to be able to provide it.
ResourceType = _tx.TypedDict(
    "ResourceType",
    {
        "namespace": str,
        "async": _t.Union[bool, _t.Literal["eager", "lazy"]],
        "dynamic": bool,
        "relative_package_path": str,
        "external_url": str,
        "dev_package_path": str,
        "absolute_path": str,
        "asset_path": str,
        "external_only": bool,
        "filepath": str,
        "dev_only": bool,
    },
    total=False,
)


# pylint: disable=too-few-public-methods
class ResourceConfig:
    def __init__(self, serve_locally, eager_loading):
        self.eager_loading = eager_loading
        self.serve_locally = serve_locally


class Resources:
    def __init__(self, resource_name: str, config: ResourceConfig):
        self._resources: _t.List[ResourceType] = []
        self.resource_name = resource_name
        self.config = config

    def append_resource(self, resource: ResourceType):
        self._resources.append(resource)

    # pylint: disable=too-many-branches
    def _filter_resources(
        self, all_resources: _t.List[ResourceType], dev_bundles=False
    ):
        filtered_resources = []
        for s in all_resources:
            filtered_resource = {}
            valid_resource = True
            if "dynamic" in s:
                filtered_resource["dynamic"] = s["dynamic"]
            if "async" in s:
                if "dynamic" in s:
                    raise exceptions.ResourceException(
                        f"""
                        Can't have both 'dynamic' and 'async'.
                        {json.dumps(filtered_resource)}
                        """
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

            if "external_url" in s and (
                s.get("external_only") or not self.config.serve_locally
            ):
                filtered_resource["external_url"] = s["external_url"]
            elif "dev_package_path" in s and (dev_bundles or s.get("dev_only")):
                if dev_bundles:
                    filtered_resource["relative_package_path"] = s["dev_package_path"]
                else:
                    valid_resource = False
            elif "relative_package_path" in s:
                filtered_resource["relative_package_path"] = s["relative_package_path"]
            elif "absolute_path" in s:
                filtered_resource["absolute_path"] = s["absolute_path"]
            elif "asset_path" in s:
                info = os.stat(s["filepath"])  # type: ignore
                filtered_resource["asset_path"] = s["asset_path"]
                filtered_resource["ts"] = info.st_mtime
            elif self.config.serve_locally:
                warnings.warn(
                    (
                        "You have set your config to `serve_locally=True` but "
                        f"A local version of {s.get('external_url', '')} is not available.\n"  # type: ignore
                        "If you added this file with "
                        "`app.scripts.append_script` "
                        "or `app.css.append_css`, use `external_scripts` "
                        "or `external_stylesheets` instead.\n"
                        "See https://dash.plotly.com/external-resources"
                    )
                )
                continue
            else:
                raise exceptions.ResourceException(
                    f"""
                    {json.dumps(filtered_resource)} does not have a
                    relative_package_path, absolute_path, or an external_url.
                    """
                )

            if valid_resource:
                filtered_resources.append(filtered_resource)

        return filtered_resources

    def get_all_resources(self, dev_bundles=False):
        lib_resources = ComponentRegistry.get_resources(self.resource_name)
        all_resources = lib_resources + self._resources

        return self._filter_resources(all_resources, dev_bundles)

    def get_library_resources(self, libraries, dev_bundles=False):
        lib_resources = ComponentRegistry.get_resources(self.resource_name, libraries)
        all_resources = lib_resources + self._resources

        return self._filter_resources(all_resources, dev_bundles)


class Css:
    def __init__(self, serve_locally: bool):
        self.config = ResourceConfig(serve_locally, True)
        self._resources = Resources("_css_dist", self.config)

    def append_css(self, stylesheet: ResourceType):
        self._resources.append_resource(stylesheet)

    def get_all_css(self):
        return self._resources.get_all_resources()

    def get_library_css(self, libraries: _t.List[str]):
        return self._resources.get_library_resources(libraries)


class Scripts:
    def __init__(self, serve_locally, eager):
        self.config = ResourceConfig(serve_locally, eager)
        self._resources = Resources("_js_dist", self.config)

    def append_script(self, script):
        self._resources.append_resource(script)

    def get_all_scripts(self, dev_bundles=False):
        return self._resources.get_all_resources(dev_bundles)

    def get_library_scripts(self, libraries, dev_bundles=False):
        return self._resources.get_library_resources(libraries, dev_bundles)
