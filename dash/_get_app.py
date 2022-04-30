APP = None


def get_app():
    if APP is None:
        raise Exception(
            "get_app() must be called after the app has started. TODO make better error message"
        )
    return APP
