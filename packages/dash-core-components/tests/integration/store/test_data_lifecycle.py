import dash.testing.wait as wait


def test_stdl001_data_lifecycle_with_different_condition(store_app, dash_dcc):
    dash_dcc.start_server(store_app)

    nclicks = 10
    dash_dcc.multiple_click("#btn", nclicks)

    dash_dcc.wait_for_text_to_equal(
        "#output", '{{"n_clicks": {}}}'.format(nclicks)
    )
    assert dash_dcc.get_local_storage() == {
        "n_clicks": nclicks
    }, "local storage should contain the same click nums"
    assert dash_dcc.get_session_storage() == {
        "n_clicks": nclicks
    }, "session storage should contain the same click nums"

    dash_dcc.driver.refresh()
    assert dash_dcc.find_element("#output").text == '"{}"'.format(
        store_app.uuid
    ), "a browser refresh will clear the memory type data to initial data"
    assert dash_dcc.get_local_storage() == {"n_clicks": nclicks}
    assert dash_dcc.get_session_storage() == {"n_clicks": nclicks}

    dash_dcc.open_new_tab()
    dash_dcc.toggle_window()  # switch to the new tab
    assert dash_dcc.get_local_storage() == {
        "n_clicks": nclicks
    }, "local storage should be persistent"
    assert dash_dcc.find_element("#output").text == '"{}"'.format(
        store_app.uuid
    ), "memory storage should contain the initial data in new tab"

    dash_dcc.multiple_click("#btn", 2)
    wait.until(lambda: dash_dcc.get_session_storage() == {"n_clicks": 2}, timeout=1)
    assert (
        '"n_clicks": 2' in dash_dcc.wait_for_element("#output").text
    ), "memory storage should reflect to the new clicks"

    dash_dcc.driver.close()
    dash_dcc.switch_window()
    assert dash_dcc.get_local_storage() == {"n_clicks": 2}
    assert dash_dcc.find_element("#output").text == '"{}"'.format(
        store_app.uuid
    ), "memory output should be the same as after previous refresh"
    assert dash_dcc.get_session_storage() == {
        "n_clicks": nclicks
    }, "session storage should be specific per browser tab window"
