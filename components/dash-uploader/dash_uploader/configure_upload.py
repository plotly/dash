import logging

import dash_uploader.settings as settings
from dash_uploader.upload import update_upload_api
from dash_uploader.httprequesthandler import HttpRequestHandler


logger = logging.getLogger("dash_uploader")


def configure_upload(
    app, folder, use_upload_id=True, upload_api=None, http_request_handler=None
):
    r"""
    Configure the upload APIs for dash app.
    This function is required to be called before using du.callback.

    Parameters
    ---------
    app: dash.Dash
        The application instance
    folder: str
        The folder where to upload files.
        Can be relative ("uploads") or
        absolute (r"C:\tmp\my_uploads").
        If the folder does not exist, it will
        be created automatically.
    use_upload_id: bool
        Determines if the uploads are put into
        folders defined by a "upload id" (upload_id).
        If True, uploads will be put into `folder`/<upload_id>/;
        that is, every user (for example with different
        session id) will use their own folder. If False,
        all files from all sessions are uploaded into
        same folder (not recommended).
    upload_api: None or str
        The upload api endpoint to use; the url that is used
        internally for the upload component POST and GET HTTP
        requests. For example: "/API/dash-uploader"
    http_request_handler: None or class
        Used for custom configuration on the Http POST and GET requests.
        This can be used to add validation for the HTTP requests (Important
        if your site is public!). If None, dash_uploader.HttpRequestHandler is used.
        If you provide a class, use a subclass of HttpRequestHandler.
        See the documentation of dash_uploader.HttpRequestHandler for
        more details.
    """
    settings.UPLOAD_FOLDER_ROOT = folder
    settings.app = app

    if upload_api is None:
        upload_api = settings.upload_api
    else:
        # Set the upload api since du.Upload components
        # that are created after du.configure_upload
        # need to be able to read the api endpoint.
        settings.upload_api = upload_api

    # Needed if using a proxy
    settings.requests_pathname_prefix = app.config.get("requests_pathname_prefix", "/")
    settings.routes_pathname_prefix = app.config.get("routes_pathname_prefix", "/")

    upload_api = update_upload_api(settings.routes_pathname_prefix, upload_api)

    if http_request_handler is None:
        http_request_handler = HttpRequestHandler

    decorate_server(
        app.server,
        folder,
        upload_api,
        http_request_handler=http_request_handler,
        use_upload_id=use_upload_id,
    )


def decorate_server(
    server,
    temp_base,
    upload_api,
    http_request_handler,
    use_upload_id=True,
):
    """
    Parameters
    ----------
    server: flask.Flask
        The flask server instance
    temp_base: str
        The upload root folder
    upload_api: str
        The upload api endpoint to use; the url that is used
        internally for the upload component POST and GET HTTP
        requests.
    use_upload_id: bool
        Determines if the uploads are put into
        folders defined by a "upload id" (upload_id).
        If True, uploads will be put into `folder`/<upload_id>/;
        that is, every user (for example with different
        session id) will use their own folder. If False,
        all files from all sessions are uploaded into
        same folder (not recommended).
    """

    handler = http_request_handler(
        server, upload_folder=temp_base, use_upload_id=use_upload_id
    )

    server.add_url_rule(upload_api, None, handler.get, methods=["GET"])
    server.add_url_rule(upload_api, None, handler.post, methods=["POST"])
