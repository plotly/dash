import dash
import dash_core_components
import dash_core_components as dcc
import dash_html_components as html
import importlib
import multiprocessing
import percy
import time
import unittest
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class IntegrationTests(unittest.TestCase):

    last_timestamp = 0


    def percy_snapshot(self, name=''):
        snapshot_name = '{} - py{}.{}'.format(name, sys.version_info.major, sys.version_info.minor)
        print(snapshot_name)
        self.percy_runner.snapshot(
            name=snapshot_name
        )
        self.driver.save_screenshot('/tmp/artifacts/{}.png'.format(name))

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()

        options = Options()
        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = {'browser': 'SEVERE'}

        if 'DASH_TEST_CHROMEPATH' in os.environ:
            options.binary_location = os.environ['DASH_TEST_CHROMEPATH']

        cls.driver = webdriver.Chrome(
            options=options, desired_capabilities=capabilities)

        loader = percy.ResourceLoader(webdriver=cls.driver)
        cls.percy_runner = percy.Runner(loader=loader)

        cls.percy_runner.initialize_build()


    @classmethod
    def tearDownClass(cls):
        super(IntegrationTests, cls).tearDownClass()
        cls.driver.quit()
        cls.percy_runner.finalize_build()

    def setUp(self):
        pass

    def tearDown(self):
        time.sleep(2)
        self.server_process.terminate()
        time.sleep(2)

        self.clear_log()
        time.sleep(1)

    def startServer(self, dash, **kwargs):
        def run():
            dash.scripts.config.serve_locally = True
            dash.css.config.serve_locally = True
            kws = dict(
                port=8050,
                debug=False,
                processes=4,
                threaded=False
            )
            kws.update(kwargs)
            dash.run_server(**kws)

        # Run on a separate process so that it doesn't block
        self.server_process = multiprocessing.Process(target=run)
        self.server_process.start()
        time.sleep(0.5)

        # Visit the dash page
        self.driver.implicitly_wait(2)
        self.driver.get('http://localhost:8050')

    def clear_log(self):
        entries = self.driver.get_log("browser")
        if entries:
            self.last_timestamp = entries[-1]["timestamp"]

    def get_log(self):
        entries = self.driver.get_log("browser")
        return [entry for entry in entries if entry["timestamp"] > self.last_timestamp]

    def wait_until_get_log(self, timeout=10):
        logs = None
        cnt, poll = 0, 0.1
        while not logs:
            logs = self.get_log()
            print(cnt, ' => ', logs)
            time.sleep(poll)
            cnt += 1
            if cnt * poll >= timeout * 1000:
                raise TimeoutError('cannot get log in {}'.format(timeout))

        return logs

    def is_console_clean(self):
        return not self.get_log()