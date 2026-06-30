import packaging
import pkg_resources

## Dash version
dash_version_str = pkg_resources.get_distribution("dash").version
dash_version = packaging.version.parse(dash_version_str)


def dash_version_is_greater_or_equal_to(version):
    """
    Check if the installed version of Dash is
    greater or equal than some version.

    Parameters
    ----------
    version: str
        The version string. E.g. '1.14.0'
    """
    return dash_version >= packaging.version.parse(version)
