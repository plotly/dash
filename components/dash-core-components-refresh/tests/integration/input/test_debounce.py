from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import pytest


def test_debounce_text_by_time(dash_dcc, debounce_text_app):
    dash_dcc.start_server(debounce_text_app)

    # expect that a long debounce does not call back in a short amount of time
    elem = dash_dcc.find_element("#input-slow")
    elem.send_keys("unit test slow")
    with pytest.raises(TimeoutException):
        WebDriverWait(dash_dcc.driver, timeout=1).until(
            lambda d: d.find_element(By.XPATH, "//*[text()='unit test slow']")
        )

    # but do expect that it is eventually called
    dash_dcc.wait_for_text_to_equal(
        "#div-slow", "unit test slow"
    ), "long debounce is eventually called back"

    # expect that a short debounce calls back within a short amount of time
    elem = dash_dcc.find_element("#input-fast")
    elem.send_keys("unit test fast")
    WebDriverWait(dash_dcc.driver, timeout=1).until(
        lambda d: d.find_element(By.XPATH, "//*[text()='unit test fast']")
    )

    assert dash_dcc.get_logs() == []


def test_debounce_number_by_time(dash_dcc, debounce_number_app):
    dash_dcc.start_server(debounce_number_app)

    # expect that a long debounce does not call back in a short amount of time
    elem = dash_dcc.find_element("#input-slow")
    elem.send_keys("12345")
    with pytest.raises(TimeoutException):
        WebDriverWait(dash_dcc.driver, timeout=1).until(
            lambda d: d.find_element(By.XPATH, "//*[text()='12345']")
        )

    # but do expect that it is eventually called
    dash_dcc.wait_for_text_to_equal(
        "#div-slow", "12345"
    ), "long debounce is eventually called back"

    # expect that a short debounce calls back within a short amount of time
    elem = dash_dcc.find_element("#input-fast")
    elem.send_keys("10000")
    WebDriverWait(dash_dcc.driver, timeout=1).until(
        lambda d: d.find_element(By.XPATH, "//*[text()='10000']")
    )

    assert dash_dcc.get_logs() == []
