from ._utils import AttributeDict
from . import exceptions

CONFIG = AttributeDict()


def get_asset_url(path):
    return app_get_asset_url(CONFIG, path)


def app_get_asset_url(config, path):
    if config.assets_external_path:
        prefix = config.assets_external_path
    else:
        prefix = config.requests_pathname_prefix
    return "/".join(
        [
            # Only take the first part of the pathname
            prefix.rstrip("/"),
            config.assets_url_path.lstrip("/"),
            path,
        ]
    )


def get_relative_path(path):
    """
    Return a path with `requests_pathname_prefix` prefixed before it.
    Use this function when specifying local URL paths that will work
    in environments regardless of what `requests_pathname_prefix` is.
    In some deployment environments, like Dash Enterprise,
    `requests_pathname_prefix` is set to the application name,
    e.g. `my-dash-app`.
    When working locally, `requests_pathname_prefix` might be unset and
    so a relative URL like `/page-2` can just be `/page-2`.
    However, when the app is deployed to a URL like `/my-dash-app`, then
    `app.get_relative_path('/page-2')` will return `/my-dash-app/page-2`.
    This can be used as an alternative to `get_asset_url` as well with
    `app.get_relative_path('/assets/logo.png')`

    Use this function with `app.strip_relative_path` in callbacks that
    deal with `dcc.Location` `pathname` routing.
    That is, your usage may look like:
    ```
    app.layout = html.Div([
        dcc.Location(id='url'),
        html.Div(id='content')
    ])
    @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
    def display_content(path):
        page_name = app.strip_relative_path(path)
        if not page_name:  # None or ''
            return html.Div([
                dcc.Link(href=app.get_relative_path('/page-1')),
                dcc.Link(href=app.get_relative_path('/page-2')),
            ])
        elif page_name == 'page-1':
            return chapters.page_1
        if page_name == "page-2":
            return chapters.page_2
    ```
    """
    return app_get_relative_path(CONFIG.requests_pathname_prefix, path)


def app_get_relative_path(requests_pathname, path):
    if requests_pathname == "/" and path == "":
        return "/"
    if requests_pathname != "/" and path == "":
        return requests_pathname
    if not path.startswith("/"):
        raise exceptions.UnsupportedRelativePath(
            f"""
            Paths that aren't prefixed with a leading / are not supported.
            You supplied: {path}
            """
        )
    return "/".join([requests_pathname.rstrip("/"), path.lstrip("/")])


def strip_relative_path(path):
    """
    Return a path with `requests_pathname_prefix` and leading and trailing
    slashes stripped from it. Also, if None is passed in, None is returned.
    Use this function with `get_relative_path` in callbacks that deal
    with `dcc.Location` `pathname` routing.
    That is, your usage may look like:
    ```
    app.layout = html.Div([
        dcc.Location(id='url'),
        html.Div(id='content')
    ])
    @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
    def display_content(path):
        page_name = app.strip_relative_path(path)
        if not page_name:  # None or ''
            return html.Div([
                dcc.Link(href=app.get_relative_path('/page-1')),
                dcc.Link(href=app.get_relative_path('/page-2')),
            ])
        elif page_name == 'page-1':
            return chapters.page_1
        if page_name == "page-2":
            return chapters.page_2
    ```
    Note that `chapters.page_1` will be served if the user visits `/page-1`
    _or_ `/page-1/` since `strip_relative_path` removes the trailing slash.

    Also note that `strip_relative_path` is compatible with
    `get_relative_path` in environments where `requests_pathname_prefix` set.
    In some deployment environments, like Dash Enterprise,
    `requests_pathname_prefix` is set to the application name, e.g. `my-dash-app`.
    When working locally, `requests_pathname_prefix` might be unset and
    so a relative URL like `/page-2` can just be `/page-2`.
    However, when the app is deployed to a URL like `/my-dash-app`, then
    `app.get_relative_path('/page-2')` will return `/my-dash-app/page-2`

    The `pathname` property of `dcc.Location` will return '`/my-dash-app/page-2`'
    to the callback.
    In this case, `app.strip_relative_path('/my-dash-app/page-2')`
    will return `'page-2'`

    For nested URLs, slashes are still included:
    `app.strip_relative_path('/page-1/sub-page-1/')` will return
    `page-1/sub-page-1`
    ```
    """
    return app_strip_relative_path(CONFIG.requests_pathname_prefix, path)


def app_strip_relative_path(requests_pathname, path):
    if path is None:
        return None
    if (
        requests_pathname != "/" and not path.startswith(requests_pathname.rstrip("/"))
    ) or (requests_pathname == "/" and not path.startswith("/")):
        raise exceptions.UnsupportedRelativePath(
            f"""
            Paths that aren't prefixed with requests_pathname_prefix are not supported.
            You supplied: {path} and requests_pathname_prefix was {requests_pathname}
            """
        )
    if requests_pathname != "/" and path.startswith(requests_pathname.rstrip("/")):
        path = path.replace(
            # handle the case where the path might be `/my-dash-app`
            # but the requests_pathname_prefix is `/my-dash-app/`
            requests_pathname.rstrip("/"),
            "",
            1,
        )
    return path.strip("/")
