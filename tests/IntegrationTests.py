import multiprocessing
import sys
import time
import unittest
import percy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIMEOUT = 20


class IntegrationTests(unittest.TestCase):

    def percy_snapshot(cls, name=''):
        snapshot_name = '{} - {}'.format(name, sys.version_info)
        print(snapshot_name)
        cls.percy_runner.snapshot(
            name=snapshot_name
        )

    def wait_for_element_by_css_selector(self, selector):
        return WebDriverWait(self.driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def wait_for_text_to_equal(self, selector, assertion_text):
        return WebDriverWait(self.driver, TIMEOUT).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector),
                                             assertion_text)
        )

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()
        cls.driver = webdriver.Chrome()

        loader = percy.ResourceLoader(
            webdriver=cls.driver,
            base_url='/assets',
            root_dir='tests/assets'
        )
        cls.percy_runner = percy.Runner(loader=loader)

        cls.percy_runner.initialize_build()

    @classmethod
    def tearDownClass(cls):
        super(IntegrationTests, cls).tearDownClass()
        cls.driver.quit()
        cls.percy_runner.finalize_build()

    def setUp(s):
        pass

    def tearDown(s):
        if hasattr(s, 'server_process'):
            time.sleep(2)
            s.server_process.terminate()
            time.sleep(2)

    def startServer(s, dash):
        def run():
            dash.scripts.config.serve_locally = True
            dash.run_server(
                port=8050,
                debug=False,
                processes=4,
                threaded=False
            )

        # Run on a separate process so that it doesn't block
        s.server_process = multiprocessing.Process(target=run)
        s.server_process.start()
        time.sleep(0.5)

        # Visit the dash page
        s.driver.get('http://localhost:8050')
        time.sleep(0.5)

        # Inject an error and warning logger
        logger = '''
        window.tests = {};
        window.tests.console = {error: [], warn: [], log: []};

        var _log = console.log;
        var _warn = console.warn;
        var _error = console.error;

        console.log = function() {
            window.tests.console.log.push({method: 'log', arguments: arguments});
            return _log.apply(console, arguments);
        };

        console.warn = function() {
            window.tests.console.warn.push({method: 'warn', arguments: arguments});
            return _warn.apply(console, arguments);
        };

        console.error = function() {
            window.tests.console.error.push({method: 'error', arguments: arguments});
            return _error.apply(console, arguments);
        };
        '''
        s.driver.execute_script(logger)
