from textwrap import dedent

APP = None


def get_app():
    if APP is None:
        raise Exception(
            dedent(
                """
                App object is not yet defined.  `app = dash.Dash()` needs to be run
                before `dash.get_app()` is called and can only be used within apps that use
                the `pages` multi-page app feature: `dash.Dash(use_pages=True)`.

                `dash.get_app()` is used to get around circular import issues when Python files
                within the pages/` folder need to reference the `app` object.
                """
            )
        )
    return APP
