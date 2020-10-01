from dash.testing.browser import Browser


class DashComposite(Browser):
    def __init__(self, server, **kwargs):
        super(DashComposite, self).__init__(**kwargs)
        self.server = server

    def start_server(self, app, **kwargs):
        """Start the local server with app."""

        load_url = kwargs.get("load_url", True)
        kwargs.pop("load_url", None)

        # start server with app and pass Dash arguments
        self.server(app, **kwargs)

        # set the default server_url, it implicitly call wait_for_page
        if load_url:
            self.server_url = self.server.url
        else:
            self.pure_server_url = self.server.url


class DashRComposite(Browser):
    def __init__(self, server, **kwargs):
        super(DashRComposite, self).__init__(**kwargs)
        self.server = server

    def start_server(self, app, cwd=None):

        # start server with dashR app. The app sets its own run_server args
        # on the R side, but we support overriding the automatic cwd
        self.server(app, cwd=cwd)

        # set the default server_url, it implicitly call wait_for_page
        self.server_url = self.server.url


class DashJuliaComposite(Browser):
    def __init__(self, server, **kwargs):
        super(DashJuliaComposite, self).__init__(**kwargs)
        self.server = server

    def start_server(self, app, cwd=None):
        # start server with Dash.jl app. The app sets its own run_server args
        # on the Julia side, but we support overriding the automatic cwd
        self.server(app, cwd=cwd)

        # set the default server_url, it implicitly call wait_for_page
        self.server_url = self.server.url
