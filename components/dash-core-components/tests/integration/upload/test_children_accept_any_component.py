import time
from dash import Dash, dcc, html


def test_upca001_upload_children_gallery(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="waitfor"),
            html.Label("Empty"),
            dcc.Upload(),
            html.Label("Button"),
            dcc.Upload(html.Button("Upload File")),
            html.Label("Text"),
            dcc.Upload("Upload File"),
            html.Label("Link"),
            dcc.Upload(html.A("Upload File")),
            html.Label("Style"),
            dcc.Upload(
                ["Drag and Drop or ", html.A("Select a File")],
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                },
            ),
            dcc.Upload(
                "upload",
                disabled=True,
                className_disabled="upload-disabled",
                id="upload",
            ),
            dcc.Upload("upload", disabled=True, id="upload-no-className"),
        ]
    )
    dash_dcc.start_server(app)
    time.sleep(0.5)
    dash_dcc.percy_snapshot("upca001 children gallery")

    first_child = dash_dcc.find_element("#upload").find_element_by_css_selector(
        ":first-child"
    )
    # Check that there is no default style since className is specified
    style = first_child.get_attribute("style")
    assert "opacity: 0.5" not in style

    first_child = dash_dcc.find_element(
        "#upload-no-className"
    ).find_element_by_css_selector(":first-child")

    # Check that there is default style since no className is specified
    style = first_child.get_attribute("style")
    assert "opacity: 0.5" in style

    assert dash_dcc.get_logs() == []
