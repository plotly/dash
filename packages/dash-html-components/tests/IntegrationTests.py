import multiprocessing
import sys
import time
import unittest
from selenium import webdriver
import percy


class IntegrationTests(unittest.TestCase):

    def percy_snapshot(cls, name=''):
        snapshot_name = '{} - py{}.{}'.format(name, sys.version_info.major, sys.version_info.minor)
        print(snapshot_name)
        cls.percy_runner.snapshot(
            name=snapshot_name
        )

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()
        cls.driver = webdriver.Chrome()

        loader = percy.ResourceLoader(
            webdriver=cls.driver
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

        # Visit the Dash page
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
