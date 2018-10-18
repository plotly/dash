import os

# noinspection PyCompatibility
from . import exceptions
from ._utils import AttributeDict


def env_configs():
    """
    Configs from the environ.

    :return: A dict with the dash environ vars
    """
    return AttributeDict({x: os.getenv(x, os.getenv(x.lower())) for x in (
        'DASH_APP_NAME',
        'DASH_URL_BASE_PATHNAME',
        'DASH_ROUTES_PATHNAME_PREFIX',
        'DASH_REQUESTS_PATHNAME_PREFIX',
        'DASH_SUPPRESS_CALLBACK_EXCEPTIONS',
        'DASH_ASSETS_EXTERNAL_PATH',
        'DASH_INCLUDE_ASSETS_FILES',
        'DASH_COMPONENTS_CACHE_MAX_AGE',
        'DASH_INCLUDE_ASSETS_FILES',
        'DASH_SERVE_DEV_BUNDLES',
        'DASH_DEBUG'
    )})


def get_config(config_name, init, env, default=None, is_bool=False):
    if init is not None:
        return init

    env_value = env.get('DASH_{}'.format(config_name.upper()))
    if env_value is None:
        return default
    return env_value if not is_bool else env_value.lower() == 'true'


def pathname_configs(url_base_pathname=None,
                     routes_pathname_prefix=None,
                     requests_pathname_prefix=None,
                     environ_configs=None):
    _pathname_config_error_message = '''
    {} This is ambiguous.
    To fix this, set `routes_pathname_prefix` instead of `url_base_pathname`.

    Note that `requests_pathname_prefix` is the prefix for the AJAX calls that
    originate from the client (the web browser) and `routes_pathname_prefix` is
    the prefix for the API routes on the backend (this flask server).
    `url_base_pathname` will set `requests_pathname_prefix` and
    `routes_pathname_prefix` to the same value.
    If you need these to be different values then you should set
    `requests_pathname_prefix` and `routes_pathname_prefix`,
    not `url_base_pathname`.
    '''
    environ_configs = environ_configs or env_configs()

    url_base_pathname = get_config('url_base_pathname',
                                   url_base_pathname,
                                   environ_configs)

    routes_pathname_prefix = get_config('routes_pathname_prefix',
                                        routes_pathname_prefix,
                                        environ_configs)

    requests_pathname_prefix = get_config('requests_pathname_prefix',
                                          requests_pathname_prefix,
                                          environ_configs)

    if url_base_pathname is not None and requests_pathname_prefix is not None:
        raise exceptions.InvalidConfig(
            _pathname_config_error_message.format(
                'You supplied `url_base_pathname` and '
                '`requests_pathname_prefix`.'
            )
        )
    elif url_base_pathname is not None and routes_pathname_prefix is not None:
        raise exceptions.InvalidConfig(
            _pathname_config_error_message.format(
                'You supplied `url_base_pathname` and '
                '`routes_pathname_prefix`.')
        )
    elif url_base_pathname is not None and routes_pathname_prefix is None:
        routes_pathname_prefix = url_base_pathname
    elif routes_pathname_prefix is None:
        routes_pathname_prefix = '/'

    if not routes_pathname_prefix.startswith('/'):
        raise exceptions.InvalidConfig(
            '`routes_pathname_prefix` needs to start with `/`')
    if not routes_pathname_prefix.endswith('/'):
        raise exceptions.InvalidConfig(
            '`routes_pathname_prefix` needs to end with `/`')

    app_name = environ_configs.DASH_APP_NAME

    if not requests_pathname_prefix and app_name:
        requests_pathname_prefix = '/' + app_name + routes_pathname_prefix
    elif requests_pathname_prefix is None:
        requests_pathname_prefix = routes_pathname_prefix

    if not requests_pathname_prefix.endswith(routes_pathname_prefix):
        raise exceptions.InvalidConfig(
            '`requests_pathname_prefix` needs to ends with '
            '`routes_pathname_prefix`.'
        )

    return url_base_pathname, routes_pathname_prefix, requests_pathname_prefix
