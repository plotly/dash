import multiprocessing
import sys
import time
import unittest
import threading
import platform
import percy
import flask
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IntegrationTests(unittest.TestCase):

    def percy_snapshot(cls, name=''):
        snapshot_name = '{} - {}'.format(name, sys.version_info)
        print(snapshot_name)
        cls.percy_runner.snapshot(
            name=snapshot_name
        )

    def wait_for_element_by_id(self, _id):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, _id))
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

    def setUp(self):
        pass

    def tearDown(self):
        time.sleep(2)
        if platform.system() == 'Windows':
            requests.get('http://localhost:8050/stop')
            time.sleep(4)
        else:
            self.server_process.terminate()
        time.sleep(2)

    def startServer(self, dash):
        def run():
            dash.scripts.config.serve_locally = True
            dash.run_server(
                port=8050,
                debug=False,
                processes=4,
                threaded=False
            )

        def run_windows():
            dash.scripts.config.serve_locally = True
            dash.css.config.serve_locally = True

            @dash.server.route('/stop')
            def _stop_server_windows():
                stopper = flask.request.environ['werkzeug.server.shutdown']
                stopper()
                return 'stop'

            dash.run_server(
                port=8050,
                debug=False,
                dev_mode=True,
                threaded=True
            )

        # Run on a separate process so that it doesn't block
        system = platform.system()
        if system == 'Windows':
            # multiprocess can't pickle an inner func on windows (closure are not serializable by default on windows)
            self.server_thread = threading.Thread(target=run_windows)
            self.server_thread.start()
        else:
            self.server_process = multiprocessing.Process(target=run)
            self.server_process.start()
        time.sleep(3)

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
