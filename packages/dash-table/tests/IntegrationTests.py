import os
import multiprocessing
import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import percy
import logging

# flake8: noqa: F401
# pylint: disable=import-error,unused-import
import chromedriver_binary

PERCY_ENABLED = False


class IntegrationTests(unittest.TestCase):

    def percy_snapshot(self, name=''):
        if PERCY_ENABLED:
            snapshot_name = '{} - {}'.format(name, sys.version_info)
            self.percy_runner.snapshot(
                name=snapshot_name
            )

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()

        options = Options()
        if 'DASH_TEST_CHROMEPATH' in os.environ:
            options.binary_location = os.environ['DASH_TEST_CHROMEPATH']

        cls.driver = webdriver.Chrome(chrome_options=options)

        if PERCY_ENABLED:
            loader = percy.ResourceLoader(
                webdriver=cls.driver
            )
            cls.percy_runner = percy.Runner(loader=loader)
            cls.percy_runner.initialize_build()

    @classmethod
    def tearDownClass(cls):
        super(IntegrationTests, cls).tearDownClass()

        if PERCY_ENABLED:
            cls.driver.quit()
            cls.percy_runner.finalize_build()

    def setUp(self):
        pass

    def tearDown(self):
        time.sleep(2)
        self.server_process.terminate()
        time.sleep(2)

    def startServer(self, app):
        def run():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True
            app.run_server(
                port=8050,
                debug=False,
                processes=1,
                threaded=True
            )

        # Run on a separate process so that it doesn't block
        self.server_process = multiprocessing.Process(target=run)
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        self.server_process.start()
        time.sleep(5)

        # Visit the dash page
        self.driver.get('http://localhost:8050')
        time.sleep(0.5)

        # Inject an error and warning logger
        logger = '''
        window.tests = {};
        window.tests.console = {error: [], warn: [], log: []};

        var _log = console.log;
        var _warn = console.warn;
        var _error = console.error;

        console.log = function() {
            window.tests.console.log.push({
                method: 'log', arguments: arguments
            });
            return _log.apply(console, arguments);
        };

        console.warn = function() {
            window.tests.console.warn.push({
                method: 'warn', arguments: arguments
            });
            return _warn.apply(console, arguments);
        };

        console.error = function() {
            window.tests.console.error.push({
                method: 'error', arguments: arguments
            });
            return _error.apply(console, arguments);
        };
        '''
        self.driver.execute_script(logger)
