from selenium import webdriver


def pytest_setup_options():
    options = webdriver.ChromeOptions()
    # Removes a bunch of errors on Windows, like
    # USB: usb_device_win.cc:93 Failed to read descriptors from ...
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return options
