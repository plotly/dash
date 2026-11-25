from dash.testing.wait import until


def wait_for_search_focus(dash_duo):
    # The dropdown focuses its search input one animation frame after opening.
    dash_duo.wait_for_element(".dash-dropdown-search")
    until(
        lambda: dash_duo.driver.execute_script(
            "return document.activeElement.type === 'search';"
        ),
        timeout=4,
    )


def focused_option_text(dash_duo):
    return dash_duo.driver.execute_script(
        """
        const option = document.activeElement?.closest('.dash-options-list-option');
        return option ? option.textContent.trim() : null;
        """
    )


def wait_for_focused_option(dash_duo, text):
    # Options also take focus one animation frame after the key press.
    until(
        lambda: focused_option_text(dash_duo) == text,
        timeout=4,
        msg=f"option {text!r} never took focus",
    )
