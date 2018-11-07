from __future__ import absolute_import
import os
import multiprocessing
import time
import unittest
import percy
import threading
import platform
import flask
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class IntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()

        options = Options()

        if 'DASH_TEST_CHROMEPATH' in os.environ:
            options.binary_location = os.environ['DASH_TEST_CHROMEPATH']

        cls.driver = webdriver.Chrome(chrome_options=options)
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
        if platform.system() == 'Windows':
            requests.get('http://localhost:8050/stop')
        else:
            self.server_process.terminate()
        self.driver.back()
        time.sleep(1)

    def startServer(self, app):
        """

        :param app:
        :type app: dash.Dash
        :return:
        """
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
                processes=processes,
                threaded=False,
            )

        def run_windows():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True

            @app.server.route('/stop')
            def _stop_server_windows():
                stopper = flask.request.environ['werkzeug.server.shutdown']
                stopper()
                return 'stop'

            app.run_server(
                port=8050,
                debug=False,
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
        time.sleep(2)

        # Visit the dash page
        self.driver.get('http://localhost:8050')

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
