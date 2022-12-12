import os
from os import listdir
from os.path import isfile, join
import collections
from urllib.parse import parse_qs
from fnmatch import fnmatch
import re
import flask

from . import _validate
from ._utils import AttributeDict
from ._get_paths import get_relative_path
from ._callback_context import context_value
from ._get_app import get_app


CONFIG = AttributeDict()
PAGE_REGISTRY = collections.OrderedDict()


def _infer_image(module):
    """
    Return:
    - A page specific image: `assets/<module>.<extension>` is used, e.g. `assets/weekly_analytics.png`
    - A generic app image at `assets/app.<extension>`
    - A logo at `assets/logo.<extension>`
    """
    assets_folder = CONFIG.assets_folder
    valid_extensions = ["apng", "avif", "gif", "jpeg", "jpg", "png", "svg", "webp"]
    page_id = module.split(".")[-1]
    files_in_assets = []

    if os.path.exists(assets_folder):
        files_in_assets = [
            f for f in listdir(assets_folder) if isfile(join(assets_folder, f))
        ]
    app_file = None
    logo_file = None
    for fn in files_in_assets:
        fn_without_extension, _, extension = fn.partition(".")
        if extension.lower() in valid_extensions:
            if (
                fn_without_extension == page_id
                or fn_without_extension == page_id.replace("_", "-")
            ):
                return fn

            if fn_without_extension == "app":
                app_file = fn

            if fn_without_extension == "logo":
                logo_file = fn

    if app_file:
        return app_file

    return logo_file


def _module_name_to_page_name(filename):
    return filename.split(".")[-1].replace("_", " ").capitalize()


def _infer_path(filename, template):
    if template is None:
        if CONFIG.pages_folder:
            pages_folder = CONFIG.pages_folder.replace("\\", "/").split("/")[-1]
            path = (
                filename.replace("_", "-")
                .replace(".", "/")
                .lower()
                .split(pages_folder)[-1]
            )
        else:
            path = filename.replace("_", "-").replace(".", "/").lower()
    else:
        # replace the variables in the template with "none" to create a default path if no path is supplied
        path = re.sub("<.*?>", "none", template)
    path = "/" + path if not path.startswith("/") else path
    return path


def _parse_query_string(search):
    if search and len(search) > 0 and search[0] == "?":
        search = search[1:]
    else:
        return {}

    parsed_qs = {}
    for (k, v) in parse_qs(search).items():
        v = v[0] if len(v) == 1 else v
        parsed_qs[k] = v
    return parsed_qs


def _parse_path_variables(pathname, path_template):
    """
    creates the dict of path variables passed to the layout
    e.g. path_template= "/asset/<asset_id>"
         if pathname provided by the browser is "/assets/a100"
         returns **{"asset_id": "a100"}
    """

    # parse variable definitions e.g. <var_name> from template
    # and create pattern to match
    wildcard_pattern = re.sub("<.*?>", "*", path_template)
    var_pattern = re.sub("<.*?>", "(.*)", path_template)

    # check that static sections of the pathname match the template
    if not fnmatch(pathname, wildcard_pattern):
        return None

    # parse variable names e.g. var_name from template
    var_names = re.findall("<(.*?)>", path_template)

    # parse variables from path
    variables = re.findall(var_pattern, pathname)
    variables = variables[0] if isinstance(variables[0], tuple) else variables

    return dict(zip(var_names, variables))


def _create_redirect_function(redirect_to):
    def redirect():
        return flask.redirect(redirect_to, code=301)

    return redirect


def _set_redirect(redirect_from, path):
    app = get_app()
    if redirect_from and len(redirect_from):
        for redirect in redirect_from:
            fullname = app.get_relative_path(redirect)
            app.server.add_url_rule(
                fullname,
                fullname,
                _create_redirect_function(app.get_relative_path(path)),
            )


def register_page(
    module,
    path=None,
    path_template=None,
    name=None,
    order=None,
    title=None,
    description=None,
    image=None,
    image_url=None,
    redirect_from=None,
    layout=None,
    **kwargs,
):
    """
    Assigns the variables to `dash.page_registry` as an `OrderedDict`
    (ordered by `order`).

    `dash.page_registry` is used by `pages_plugin` to set up the layouts as
    a multi-page Dash app. This includes the URL routing callbacks
    (using `dcc.Location`) and the HTML templates to include title,
    meta description, and the meta description image.

    `dash.page_registry` can also be used by Dash developers to create the
    page navigation links or by template authors.

    - `module`:
       The module path where this page's `layout` is defined. Often `__name__`.

    - `path`:
       URL Path, e.g. `/` or `/home-page`.
       If not supplied, will be inferred from the `path_template` or `module`,
       e.g. based on path_template: `/asset/<asset_id` to `/asset/none`
       e.g. based on module: `pages.weekly_analytics` to `/weekly-analytics`

    - `relative_path`:
        The path with `requests_pathname_prefix` prefixed before it.
        Use this path when specifying local URL paths that will work
        in environments regardless of what `requests_pathname_prefix` is.
        In some deployment environments, like Dash Enterprise,
        `requests_pathname_prefix` is set to the application name,
        e.g. `my-dash-app`.
        When working locally, `requests_pathname_prefix` might be unset and
        so a relative URL like `/page-2` can just be `/page-2`.
        However, when the app is deployed to a URL like `/my-dash-app`, then
        `relative_path` will be `/my-dash-app/page-2`.

    - `path_template`:
       Add variables to a URL by marking sections with <variable_name>. The layout function
       then receives the <variable_name> as a keyword argument.
       e.g. path_template= "/asset/<asset_id>"
            then if pathname in browser is "/assets/a100" then layout will receive **{"asset_id":"a100"}

    - `name`:
       The name of the link.
       If not supplied, will be inferred from `module`,
       e.g. `pages.weekly_analytics` to `Weekly analytics`

    - `order`:
       The order of the pages in `page_registry`.
       If not supplied, then the filename is used and the page with path `/` has
       order `0`

    - `title`:
       (string or function) The name of the page <title>. That is, what appears in the browser title.
       If not supplied, will use the supplied `name` or will be inferred by module,
       e.g. `pages.weekly_analytics` to `Weekly analytics`

    - `description`:
       (string or function) The <meta type="description"></meta>.
       If not supplied, then nothing is supplied.

    - `image`:
       The meta description image used by social media platforms.
       If not supplied, then it looks for the following images in `assets/`:
        - A page specific image: `assets/<module>.<extension>` is used, e.g. `assets/weekly_analytics.png`
        - A generic app image at `assets/app.<extension>`
        - A logo at `assets/logo.<extension>`
        When inferring the image file, it will look for the following extensions:
        APNG, AVIF, GIF, JPEG, JPG, PNG, SVG, WebP.

    -  `image_url`:
       Overrides the image property and sets the `<image>` meta tag to the provided image URL.

    - `redirect_from`:
       A list of paths that should redirect to this page.
       For example: `redirect_from=['/v2', '/v3']`

    - `layout`:
       The layout function or component for this page.
       If not supplied, then looks for `layout` from within the supplied `module`.

    - `**kwargs`:
       Arbitrary keyword arguments that can be stored

    ***

    `page_registry` stores the original property that was passed in under
    `supplied_<property>` and the coerced property under `<property>`.
    For example, if this was called:
    ```
    register_page(
        'pages.historical_outlook',
        name='Our historical view',
        custom_key='custom value'
    )
    ```
    Then this will appear in `page_registry`:
    ```
    OrderedDict([
        (
            'pages.historical_outlook',
            dict(
                module='pages.historical_outlook',

                supplied_path=None,
                path='/historical-outlook',

                supplied_name='Our historical view',
                name='Our historical view',

                supplied_title=None,
                title='Our historical view'

                supplied_layout=None,
                layout=<function pages.historical_outlook.layout>,

                custom_key='custom value'
            )
        ),
    ])
    ```
    """
    if context_value.get().get("ignore_register_page"):
        return

    _validate.validate_use_pages(CONFIG)

    page = dict(
        module=_validate.validate_module_name(module),
        supplied_path=path,
        path_template=path_template,
        path=path if path is not None else _infer_path(module, path_template),
        supplied_name=name,
        name=name if name is not None else _module_name_to_page_name(module),
    )
    page.update(
        supplied_title=title,
        title=(title if title is not None else page["name"]),
    )
    page.update(
        description=description if description else "",
        order=order,
        supplied_order=order,
        supplied_layout=layout,
        **kwargs,
    )
    page.update(
        supplied_image=image,
        image=(image if image is not None else _infer_image(module)),
        image_url=image_url,
    )
    page.update(redirect_from=_set_redirect(redirect_from, page["path"]))

    PAGE_REGISTRY[module] = page

    if page["path_template"]:
        _validate.validate_template(page["path_template"])

    if layout is not None:
        # Override the layout found in the file set during `plug`
        PAGE_REGISTRY[module]["layout"] = layout

    # set home page order
    order_supplied = any(
        p["supplied_order"] is not None for p in PAGE_REGISTRY.values()
    )

    for p in PAGE_REGISTRY.values():
        p["order"] = (
            0 if p["path"] == "/" and not order_supplied else p["supplied_order"]
        )
        p["relative_path"] = get_relative_path(p["path"])

    # Sort by order and module, then by module
    for page in sorted(
        PAGE_REGISTRY.values(),
        key=lambda i: (str(i.get("order", i["module"])), i["module"]),
    ):
        PAGE_REGISTRY.move_to_end(page["module"])
