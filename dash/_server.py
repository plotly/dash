import flask

SERVER = None


def get_server(name=None):
    """
    Use `get_server() instead of `app.server` to avoid the circular `app` import issue with multi-page apps.
    """
    global SERVER  # pylint: disable=global-statement

    if SERVER is None:
        name = name if name else "__main__"
        SERVER = flask.Flask(name)
    return SERVER
