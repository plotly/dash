import dash
from dash import Dash


def test_pain001_infer_path_module_contains_folder_name(dash_duo, clear_pages_state):
    # "overviews" and "reviews" contain the pages folder name "views".
    app = Dash(__name__, use_pages=True, pages_folder="views")
    dash_duo.start_server(app)

    paths = {page["module"]: page["path"] for page in dash.page_registry.values()}
    assert paths == {
        "views.overviews": "/overviews",
        "views.reviews.latest": "/reviews/latest",
    }

    dash_duo.wait_for_page(f"{dash_duo.server_url}/overviews")
    dash_duo.wait_for_text_to_equal("#text_overviews", "text for overviews")

    dash_duo.wait_for_page(f"{dash_duo.server_url}/reviews/latest")
    dash_duo.wait_for_text_to_equal("#text_latest", "text for latest")

    assert dash_duo.get_logs() == [], "browser console should contain no error"
