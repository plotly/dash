import os
import multiprocessing
import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary  # adds chromedriver to path
import percy


PERCY_ENABLED = False


class IntegrationTests(unittest.TestCase):

    def percy_snapshot(cls, name=''):
        if PERCY_ENABLED:
            snapshot_name = '{} - {}'.format(name, sys.version_info)
            print(snapshot_name)
            cls.percy_runner.snapshot(
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

    def setUp(s):
        pass

    def tearDown(s):
        time.sleep(2)
        s.server_process.terminate()
        time.sleep(2)

    def startServer(self, app):
        if 'DASH_TEST_PROCESSES' in os.environ:
            processes = int(os.environ['DASH_TEST_PROCESSES'])
        else:
            processes = 4

        def run():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True
            app.run_server(
                port=8050,
                debug=False,
                threaded=False,
                processes=processes
            )

        # Run on a separate process so that it doesn't block
        self.server_process = multiprocessing.Process(target=run)
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
        self.driver.execute_script(logger)
