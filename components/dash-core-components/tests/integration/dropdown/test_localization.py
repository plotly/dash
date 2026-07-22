from time import sleep
from dash import Dash
from dash.dcc import Dropdown
from dash.html import Div


def test_ddlo001_translations(dash_duo):
    app = Dash(__name__)
    app.layout = Div(
        [
            Dropdown(
                id="dropdown",
                options=[1, 2, 3],
                multi=True,
                labels={
                    "select_all": "Sélectionner tout",
                    "deselect_all": "Désélectionner tout",
                    "selected_count": "{num_selected} sélections",
                    "search": "Rechercher",
                    "clear_search": "Annuler",
                    "clear_selection": "Effacer les sélections",
                    "no_options_found": "Aucun d'options",
                },
            ),
        ]
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#dropdown").click()
    dash_duo.wait_for_contains_text(
        ".dash-dropdown-action-button:first-child", "Sélectionner tout"
    )
    dash_duo.wait_for_contains_text(
        ".dash-dropdown-action-button:last-child", "Désélectionner tout"
    )

    assert (
        dash_duo.find_element(".dash-dropdown-search").accessible_name == "Rechercher"
    )

    dash_duo.find_element(".dash-dropdown-search").send_keys(1)
    sleep(0.1)
    assert dash_duo.find_element(".dash-dropdown-clear").accessible_name == "Annuler"

    dash_duo.find_element(".dash-dropdown-action-button:first-child").click()

    dash_duo.find_element(".dash-dropdown-search").send_keys(9)
    sleep(0.1)
    assert dash_duo.find_element(".dash-dropdown-option").text == "Aucun d'options"

    assert (
        dash_duo.find_element(
            ".dash-dropdown-trigger .dash-dropdown-clear"
        ).accessible_name
        == "Effacer les sélections"
    )

    assert dash_duo.get_logs() == []


def test_ddlo002_partial_translations(dash_duo):
    app = Dash(__name__)
    app.layout = Div(
        [
            Dropdown(
                id="dropdown",
                options=[1, 2, 3],
                multi=True,
                labels={
                    "search": "Lookup",
                },
            ),
        ]
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#dropdown").click()
    dash_duo.wait_for_contains_text(
        ".dash-dropdown-action-button:first-child", "Select All"
    )
    dash_duo.wait_for_contains_text(
        ".dash-dropdown-action-button:last-child", "Deselect All"
    )

    assert dash_duo.find_element(".dash-dropdown-search").accessible_name == "Lookup"

    dash_duo.find_element(".dash-dropdown-search").send_keys(1)
    sleep(0.1)
    assert (
        dash_duo.find_element(".dash-dropdown-clear").accessible_name == "Clear search"
    )

    dash_duo.find_element(".dash-dropdown-action-button:first-child").click()

    dash_duo.find_element(".dash-dropdown-search").send_keys(9)
    sleep(0.1)
    assert dash_duo.find_element(".dash-dropdown-option").text == "No options found"

    assert (
        dash_duo.find_element(
            ".dash-dropdown-trigger .dash-dropdown-clear"
        ).accessible_name
        == "Clear selection"
    )

    assert dash_duo.get_logs() == []
