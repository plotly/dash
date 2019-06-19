def test_stdl001_data_lifecycle_with_different_condition(store_app, dash_duo):
    dash_duo.start_server(store_app)

    nclicks = 10
    dash_duo.multiple_click("#btn", nclicks)

    dash_duo.wait_for_text_to_equal(
        "#output", '{{"n_clicks": {}}}'.format(nclicks)
    )
    assert dash_duo.get_local_storage() == {
        "n_clicks": nclicks
    }, "local storage should contain the same click nums"
    assert dash_duo.get_session_storage() == {
        "n_clicks": nclicks
    }, "session storage should contain the same click nums"

    dash_duo.driver.refresh()
    assert dash_duo.find_element("#output").text == '"{}"'.format(
        store_app.uuid
    ), "a browser refresh will clear the memory type data to initial data"
    assert dash_duo.get_local_storage() == {"n_clicks": nclicks}
    assert dash_duo.get_session_storage() == {"n_clicks": nclicks}

    dash_duo.open_new_tab()
    dash_duo.toggle_window()  # switch to the new tab
    assert dash_duo.get_local_storage() == {
        "n_clicks": nclicks
    }, "local storage should be persistent"
    assert dash_duo.find_element("#output").text == '"{}"'.format(
        store_app.uuid
    ), "memory storage should contain the initial data in new tab"

    dash_duo.multiple_click("#btn", 2)
    assert dash_duo.get_session_storage() == {"n_clicks": 2}
    assert (
        '"n_clicks": 2' in dash_duo.wait_for_element("#output").text
    ), "memory storage should reflect to the new clicks"

    dash_duo.driver.close()
    dash_duo.switch_window()
    assert dash_duo.get_local_storage() == {"n_clicks": 2}
    assert dash_duo.find_element("#output").text == '"{}"'.format(
        store_app.uuid
    ), "memory output should be the same as after previous refresh"
    assert dash_duo.get_session_storage() == {
        "n_clicks": nclicks
    }, "session storage should be specific per browser tab window"
