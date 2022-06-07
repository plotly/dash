import pytest
import werkzeug

import dash.testing.wait as wait


@pytest.mark.xfail(
    condition=werkzeug.__version__ in ("2.1.0", "2.1.1"),
    reason="Bug with 204 and Transfer-Encoding",
    strict=False,
)
def test_stdl001_data_lifecycle_with_different_condition(store_app, dash_dcc):
    dash_dcc.start_server(store_app)

    nclicks = 10
    dash_dcc.multiple_click("#btn", nclicks)

    dash_dcc.wait_for_text_to_equal("#output", f'{{"n_clicks": {nclicks}}}')
    assert dash_dcc.get_local_storage() == {
        "n_clicks": nclicks
    }, "local storage should contain the same click nums"
    assert dash_dcc.get_session_storage() == {
        "n_clicks": nclicks
    }, "session storage should contain the same click nums"

    dash_dcc.driver.refresh()
    dash_dcc.wait_for_text_to_equal("#output", f'"{store_app.uuid}"')
    assert dash_dcc.get_local_storage() == {"n_clicks": nclicks}
    assert dash_dcc.get_session_storage() == {"n_clicks": nclicks}

    dash_dcc.open_new_tab()
    dash_dcc.toggle_window()  # switch to the new tab
    assert dash_dcc.get_local_storage() == {
        "n_clicks": nclicks
    }, "local storage should be persistent"
    dash_dcc.wait_for_text_to_equal("#output", f'"{store_app.uuid}"')

    dash_dcc.multiple_click("#btn", 2)
    wait.until(lambda: dash_dcc.get_session_storage() == {"n_clicks": 2}, timeout=1)
    assert (
        '"n_clicks": 2' in dash_dcc.wait_for_element("#output").text
    ), "memory storage should reflect to the new clicks"

    dash_dcc.driver.close()
    dash_dcc.switch_window()
    assert dash_dcc.get_local_storage() == {"n_clicks": 2}
    dash_dcc.wait_for_text_to_equal("#output", f'"{store_app.uuid}"')
    assert dash_dcc.get_session_storage() == {
        "n_clicks": nclicks
    }, "session storage should be specific per browser tab window"

    assert dash_dcc.get_logs() == []
