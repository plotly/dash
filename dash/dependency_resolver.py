import os


class Resolver(object):

    site_packages_path = None

    def __init__(self, dependency, dependencyName):
        self.site_packages_path = self._get_site_packages_path(
            dependency,
            dependencyName
        )

    def _get_site_packages_path(self, dependency, dependencyName):
        # Get local path for site-packages
        module_path = os.path.abspath(dependency.__file__)
        module_name = dependencyName
        module_name_index = module_path.index(module_name)
        site_packages_path = module_path[:module_name_index]

        return site_packages_path

    # Support local module installations using `python setup.py install`,
    # where the module directory has
    # appended `-[MODULE_VERSION]-[pyVERSTION].egg`
    # path can be 'dash_html_components/bundle.js'
    # Resolved path can be 'dash_html_components-0.2.3-py2.7.egg/bundle.js'
    def resolve_dependency_name(self, path):
        # Split the path into parts
        path_parts = path.split(os.sep)
        # Package name is first part
        package_name = path_parts[0]
        # Find the real directory that matches package name
        matches = [f for f in os.listdir(self.site_packages_path)
                   if f.startswith(package_name) and
                   not f.endswith('dist-info')]

        package_dir = matches[0]

        # For local EGG installs, the package is nested underneath
        if package_dir.endswith('.egg'):
            package_dir = os.sep.join([package_dir, package_name])

        # Return original path with package name replaced by resolved name
        return os.sep.join([package_dir] + path_parts[1:])
