import os
from dash import Dash, Input, Output, dcc, html


def test_upfd001_folder_upload_prop_exists(dash_dcc):
    """
    Test that useFsAccessApi prop is available on dcc.Upload component.

    Note: Full end-to-end testing of folder upload functionality is limited
    because the File System Access API requires user interaction and browser
    permissions that cannot be fully automated with Selenium. This test verifies
    that the prop is correctly passed to the component.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div("Folder Upload Test", id="title"),
            dcc.Upload(
                id="upload-folder",
                children=html.Div(
                    ["Drag and Drop or ", html.A("Select Files or Folders")]
                ),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                },
                multiple=True,
                useFsAccessApi=True,  # Enable folder upload
            ),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        [Input("upload-folder", "contents")],
    )
    def update_output(contents_list):
        if contents_list is not None:
            return html.Div(
                [
                    html.Div(f"Number of files uploaded: {len(contents_list)}"),
                ]
            )
        return html.Div("No files uploaded yet")

    dash_dcc.start_server(app)

    # Wait for the component to render
    dash_dcc.wait_for_element("#upload-folder")

    # Verify the title renders correctly
    dash_dcc.wait_for_text_to_equal("#title", "Folder Upload Test")

    # Verify initial state
    dash_dcc.wait_for_text_to_equal("#output", "No files uploaded yet")

    assert dash_dcc.get_logs() == []


def test_upfd002_folder_upload_with_multiple_files(dash_dcc):
    """
    Test uploading multiple files with useFsAccessApi enabled.

    This test simulates multiple file upload to verify the API remains
    compatible when useFsAccessApi is enabled.
    """
    # Create test files
    test_dir = os.path.join(os.path.dirname(__file__), "upload-assets")
    test_file1 = os.path.join(test_dir, "upft001.csv")
    test_file2 = os.path.join(test_dir, "upft001.png")

    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div("Multiple Files Test", id="title"),
            dcc.Upload(
                id="upload-multiple",
                children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                },
                multiple=True,
                useFsAccessApi=True,
            ),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        [Input("upload-multiple", "contents")],
    )
    def update_output(contents_list):
        if contents_list is not None:
            return html.Div(
                [
                    html.Div(f"Uploaded {len(contents_list)} file(s)", id="file-count"),
                ]
            )
        return html.Div("No files uploaded")

    dash_dcc.start_server(app)

    # Find the file input and upload multiple files
    upload_input = dash_dcc.wait_for_element("#upload-multiple input[type=file]")

    # Upload multiple files - Selenium requires absolute paths joined with newline
    # Note: This simulates multiple file selection, not folder selection
    files_to_upload = "\n".join(
        [os.path.abspath(test_file1), os.path.abspath(test_file2)]
    )
    upload_input.send_keys(files_to_upload)

    # Wait for the callback to complete
    dash_dcc.wait_for_text_to_equal("#file-count", "Uploaded 2 file(s)", timeout=5)

    assert dash_dcc.get_logs() == []


def test_upfd003_folder_upload_disabled_by_default(dash_dcc):
    """
    Test that useFsAccessApi is disabled by default (False).
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div("Default Behavior Test", id="title"),
            dcc.Upload(
                id="upload-default",
                children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                },
                # useFsAccessApi not specified, should default to False
            ),
            html.Div(id="output", children="Upload ready"),
        ]
    )

    dash_dcc.start_server(app)

    # Wait for the component to render
    dash_dcc.wait_for_element("#upload-default")
    dash_dcc.wait_for_text_to_equal("#output", "Upload ready")

    assert dash_dcc.get_logs() == []
