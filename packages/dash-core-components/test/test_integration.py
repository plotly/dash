import dash_core_components
from dash.react import Dash
import importlib
import percy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import multiprocessing
import unittest

# Download geckodriver: https://github.com/mozilla/geckodriver/releases
# And add to path:
# export PATH=$PATH:/Users/chriddyp/Repos/dash-stuff/dash-integration-tests
#
# Uses percy.io for automated screenshot tests
# export PERCY_PROJECT=plotly/dash-integration-tests
# export PERCY_TOKEN=...


class IntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()
        cls.driver = webdriver.Firefox()

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
        s.server_process.terminate()

    def startServer(s, dash):
        def run():
            dash.run_server(
                port=8050,
                debug=False,
                component_suites=[
                    'dash_core_components'
                ],
                threaded=True
            )

        # Run on a separate process so that it doesn't block
        s.server_process = multiprocessing.Process(target=run)
        s.server_process.start()
        time.sleep(0.5)

    def test_integration(s):
        dash = Dash(__name__)

        dash.layout = dash_core_components.Input(
            id='hello-world'
        )

        s.startServer(dash)
        s.driver.get('http://localhost:8050')

        el = s.driver.find_element_by_id('hello-world')

        # Take a screenshot with percy
        s.percy_runner.snapshot(name='dash_core_components')
