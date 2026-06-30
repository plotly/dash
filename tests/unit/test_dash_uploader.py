import dash
from dash import dash_uploader


def test_dash_uploader_is_exported_from_dash_root():
    assert hasattr(dash, "dash_uploader")
    assert dash.dash_uploader is dash_uploader
    assert hasattr(dash_uploader, "configure_upload")
    assert hasattr(dash_uploader, "callback")
    assert hasattr(dash_uploader, "HttpRequestHandler")
    assert hasattr(dash_uploader, "Upload")


def test_dash_uploader_upload_component_factory():
    upload_component = dash_uploader.Upload()

    assert upload_component._type == "Upload_ReactComponent"
    assert upload_component._namespace == "dash_uploader"
    assert upload_component.id == "dash-uploader"
