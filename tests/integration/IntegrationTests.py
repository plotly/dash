import os
import sys
import time
import unittest
import multiprocessing

import percy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIMEOUT = 5


class SeleniumDriverTimeout(Exception):
    pass


class IntegrationTests(unittest.TestCase):

    last_timestamp = 0

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()

        options = Options()
        options.add_argument("--no-sandbox")

        capabilities = DesiredCapabilities.CHROME
        capabilities["loggingPrefs"] = {"browser": "SEVERE"}

        if "DASH_TEST_CHROMEPATH" in os.environ:
            options.binary_location = os.environ["DASH_TEST_CHROMEPATH"]

        cls.driver = webdriver.Chrome(
            options=options,
            desired_capabilities=capabilities,
            service_args=["--verbose", "--log-path=chrome.log"],
        )

        cls.percy_runner = percy.Runner(
            loader=percy.ResourceLoader(
                webdriver=cls.driver,
                base_url="/assets",
                root_dir="tests/assets",
            )
        )

        cls.percy_runner.initialize_build()

    @classmethod
    def tearDownClass(cls):
        super(IntegrationTests, cls).tearDownClass()
        cls.driver.quit()
        cls.percy_runner.finalize_build()

    def setUp(self):
        self.server_process = None

    def tearDown(self):
        try:
            time.sleep(1.5)
            self.server_process.terminate()
            time.sleep(1)
        except AttributeError:
            pass
        finally:
            self.clear_log()
            time.sleep(1)

    def startServer(self, dash, **kwargs):
        def run():
            dash.scripts.config.serve_locally = True
            dash.css.config.serve_locally = True
            kws = dict(port=8050, debug=False, processes=4, threaded=False)
            kws.update(kwargs)
            dash.run_server(**kws)

        # Run on a separate process so that it doesn't block
        self.server_process = multiprocessing.Process(target=run)
        self.server_process.start()
        time.sleep(0.5)

        # Visit the dash page
        self.driver.implicitly_wait(2)
        self.driver.get("http://localhost:8050")

    def percy_snapshot(self, name=""):
        snapshot_name = "{} - py{}.{}".format(
            name, sys.version_info.major, sys.version_info.minor
        )
        print(snapshot_name)
        self.percy_runner.snapshot(name=snapshot_name)

    def wait_for_element_by_css_selector(self, selector, timeout=TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector)),
            'Could not find element with selector "{}"'.format(selector),
        )

    def wait_for_text_to_equal(
        self, selector, assertion_text, timeout=TIMEOUT
    ):
        el = self.wait_for_element_by_css_selector(selector)
        WebDriverWait(self.driver, timeout).until(
            lambda *args: (
                (str(el.text) == assertion_text)
                or (str(el.get_attribute("value")) == assertion_text)
            ),
            "Element '{}' text was supposed to equal '{}' but it didn't".format(
                selector, assertion_text
            ),
        )

    def clear_log(self):
        entries = self.driver.get_log("browser")
        if entries:
            self.last_timestamp = entries[-1]["timestamp"]

    def get_log(self):
        entries = self.driver.get_log("browser")
        return [
            entry
            for entry in entries
            if entry["timestamp"] > self.last_timestamp
        ]

    def wait_until_get_log(self, timeout=10):

        logs = None
        cnt, poll = 0, 0.1
        while not logs:
            logs = self.get_log()
            time.sleep(poll)
            cnt += 1
            if cnt * poll >= timeout * 1000:
                raise SeleniumDriverTimeout(
                    "cannot get log in {}".format(timeout)
                )

        return logs

    def is_console_clean(self):
        return not self.get_log()
