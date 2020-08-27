from __future__ import absolute_import
import multiprocessing
import os
import platform
import threading
import time
import unittest
import percy
import flask
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()

        options = Options()
        capabilities = DesiredCapabilities.CHROME
        capabilities["loggingPrefs"] = {"browser": "SEVERE"}

        if "DASH_TEST_CHROMEPATH" in os.environ:
            options.binary_location = os.environ["DASH_TEST_CHROMEPATH"]

        cls.driver = webdriver.Chrome(
            options=options, desired_capabilities=capabilities
        )
        loader = percy.ResourceLoader(
            webdriver=cls.driver, base_url="/assets", root_dir="tests/assets"
        )
        cls.percy_runner = percy.Runner(loader=loader)
        cls.percy_runner.initialize_build()

    @classmethod
    def tearDownClass(cls):
        super(IntegrationTests, cls).tearDownClass()
        cls.driver.quit()

    def setUp(self):
        pass

    def tearDown(self):
        if platform.system() == "Windows":
            requests.get("http://localhost:8050/stop")
        else:
            self.server_process.terminate()

        self.clear_log()
        time.sleep(1)

    def startServer(self, app):
        """

        :param app:
        :type app: dash.Dash
        :return:
        """
        if "DASH_TEST_PROCESSES" in os.environ:
            processes = int(os.environ["DASH_TEST_PROCESSES"])
        else:
            processes = 4

        def run():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True
            app.run_server(
                port=8050,
                processes=processes,
                threaded=False,
                debug=True,
                use_reloader=False,
                use_debugger=True,
                dev_tools_hot_reload=False,
                dev_tools_ui=False,
            )

        def run_windows():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True

            @app.server.route("/stop")
            def _stop_server_windows():
                stopper = flask.request.environ["werkzeug.server.shutdown"]
                stopper()
                return "stop"

            app.run_server(port=8050, debug=False, threaded=True)

        # Run on a separate process so that it doesn't block

        system = platform.system()
        if system == "Windows":
            # multiprocess can't pickle an inner func on windows (closure are not serializable by default on windows)
            self.server_thread = threading.Thread(target=run_windows)
            self.server_thread.start()
        else:
            self.server_process = multiprocessing.Process(target=run)
            self.server_process.start()
        time.sleep(2)

        # Visit the dash page
        self.driver.implicitly_wait(2)
        self.driver.get("http://localhost:8050")

    def clear_log(self):
        entries = self.driver.get_log("browser")

        if entries:
            self.last_timestamp = entries[-1]["timestamp"]

    def get_log(self):
        entries = self.driver.get_log("browser")

        return [entry for entry in entries if entry["timestamp"] > self.last_timestamp]

    last_timestamp = 0
