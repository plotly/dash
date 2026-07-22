from dash import Dash, Input, Output, dcc, html


def test_upfd001_folder_upload_with_enable_folder_selection(dash_dcc):
    """
    Test that folder upload is enabled when enable_folder_selection=True.

    Note: Full end-to-end testing of folder upload functionality is limited
    by Selenium's capabilities. This test verifies the component renders
    correctly with enable_folder_selection=True which enables folder support.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div("Folder Upload Test", id="title"),
            dcc.Upload(
                id="upload-folder",
                children=html.Div(["Drag and Drop or ", html.A("Select Folder")]),
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
                enable_folder_selection=True,  # Enables folder selection
                accept=".txt,.csv",  # Test accept filtering
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
            return html.Div(f"Uploaded {len(contents_list)} file(s)", id="file-count")
        return html.Div("No files uploaded")

    dash_dcc.start_server(app)

    # Verify the component renders
    dash_dcc.wait_for_text_to_equal("#title", "Folder Upload Test")

    # Verify the upload component and input are present
    dash_dcc.wait_for_element("#upload-folder")

    # Verify the input has folder selection attributes when enable_folder_selection=True
    upload_input = dash_dcc.wait_for_element("#upload-folder input[type=file]")
    webkitdir_attr = upload_input.get_attribute("webkitdirectory")

    assert webkitdir_attr == "true", (
        f"webkitdirectory attribute should be 'true' when enable_folder_selection=True, "
        f"but got '{webkitdir_attr}'"
    )

    assert dash_dcc.get_logs() == [], "browser console should contain no error"


def test_upfd002_multiple_files_without_folder_selection(dash_dcc):
    """
    Test that multiple file upload does NOT enable folder selection
    when enable_folder_selection=False (default).
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div("Multiple Files Test", id="title"),
            dcc.Upload(
                id="upload-multiple",
                children=html.Div(
                    ["Drag and Drop or ", html.A("Select Multiple Files")]
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
                multiple=True,  # Allows multiple files
                enable_folder_selection=False,  # But NOT folder selection
                accept=".txt,.csv",  # Accept should work with file picker
            ),
            html.Div(id="output", children="Upload ready"),
        ]
    )

    dash_dcc.start_server(app)

    # Wait for the component to render
    dash_dcc.wait_for_text_to_equal("#title", "Multiple Files Test")
    dash_dcc.wait_for_text_to_equal("#output", "Upload ready")

    # Verify the input does NOT have folder selection attributes
    upload_input = dash_dcc.wait_for_element("#upload-multiple input[type=file]")
    webkitdir_attr = upload_input.get_attribute("webkitdirectory")

    # webkitdirectory should not be set when enable_folder_selection=False
    assert webkitdir_attr in [None, "", "false"], (
        f"webkitdirectory attribute should not be 'true' when enable_folder_selection=False, "
        f"but got '{webkitdir_attr}'"
    )

    # Verify multiple attribute is set
    multiple_attr = upload_input.get_attribute("multiple")
    assert multiple_attr == "true", (
        f"multiple attribute should be 'true' when multiple=True, "
        f"but got '{multiple_attr}'"
    )

    assert dash_dcc.get_logs() == [], "browser console should contain no error"


def test_upfd003_single_file_upload(dash_dcc):
    """
    Test that single file upload does NOT enable folder selection.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div("Single File Test", id="title"),
            dcc.Upload(
                id="upload-single",
                children=html.Div(["Drag and Drop or ", html.A("Select File")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                },
                multiple=False,  # Single file only
                accept="application/pdf",
            ),
            html.Div(id="output", children="Upload ready"),
        ]
    )

    dash_dcc.start_server(app)

    # Wait for the component to render
    dash_dcc.wait_for_text_to_equal("#title", "Single File Test")
    dash_dcc.wait_for_text_to_equal("#output", "Upload ready")

    # Verify the input does NOT have folder selection attributes when multiple=False
    upload_input = dash_dcc.wait_for_element("#upload-single input[type=file]")
    webkitdir_attr = upload_input.get_attribute("webkitdirectory")

    # webkitdirectory should not be set when multiple=False
    assert webkitdir_attr in [None, "", "false"], (
        f"webkitdirectory attribute should not be 'true' when multiple=False, "
        f"but got '{webkitdir_attr}'"
    )

    assert dash_dcc.get_logs() == [], "browser console should contain no error"
