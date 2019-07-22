from dash.testing.browser import Browser


class DashComposite(Browser):
    def __init__(self, server, **kwargs):
        super(DashComposite, self).__init__(**kwargs)
        self.server = server

    def start_server(self, app, **kwargs):
        """start the local server with app"""

        # start server with app and pass Dash arguments
        self.server(app, **kwargs)

        # set the default server_url, it implicitly call wait_for_page
        self.server_url = self.server.url


class DashRComposite(Browser):
    def __init__(self, server, **kwargs):
        super(DashRComposite, self).__init__(**kwargs)
        self.server = server

    def start_server(self, app):

        # start server with dashR app, the dash arguments are hardcoded
        self.server(app)

        # set the default server_url, it implicitly call wait_for_page
        self.server_url = self.server.url
