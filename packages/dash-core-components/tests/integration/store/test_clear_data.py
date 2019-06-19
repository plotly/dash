def test_stcd001_clear_data_on_all_types(store_app, dash_duo):

    dash_duo.start_server(store_app)

    assert dash_duo.wait_for_contains_text("#output", store_app.uuid)

    dash_duo.multiple_click("#btn", 3)
    assert dash_duo.get_local_storage() == {"n_clicks": 3}

    dash_duo.find_element("#clear-btn").click()

    assert (
        not dash_duo.find_element("#output").text
        and not dash_duo.get_local_storage()
        and not dash_duo.get_session_storage()
    ), "the clear_data should clear all data in three storage types"
