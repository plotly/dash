# the functionality of this test file has not been tested.
from pathlib import Path
import shutil

import chromedriver_binary
from dash.testing.application_runners import import_app
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .utils import create_file

## NOTE: Here are some notes for testing
# Naming convention: test_{tcid}_{test title}
# Running just one tcid: python -m pytest -k {tcid}
# General guide: https://dash.plotly.com/testing
# Debugging:
#  1) Add a non-existent variable to a line (like `xxx`)
#  2) Run test with --pdb flag


@pytest.fixture
def testfile10Mb_csv():
    file = Path(__file__).resolve().parent / "mytestfile.csv"
    create_file(file, filesize_mb=10)
    yield file
    file.unlink()


# Basic test for the component rendering.
# The dash_duo pytest fixture is installed with dash (v1.0+)
# Run with pytest -k render01
def test_render01_render_component(dash_duo):
    # Start a dash app contained as the variable `app` in `usage.py`
    app = import_app("usage")
    dash_duo.start_server(app)

    upload = dash_duo.find_element("#dash-uploader")

    assert "dash-uploader-default" == upload.get_attribute("class")


# Run with pytest -k upload01
def test_upload01_upload_a_file(dash_duo, testfile10Mb_csv):
    app = import_app("usage")
    dash_duo.start_server(app)

    # User sees the component
    upload = dash_duo.find_element("#dash-uploader")

    # Upload the file.
    # Clicking the upload component would open a file dialog and
    # this would require the tests to use OS specific GUI tools
    # to select the file. This could be added in the future but it's
    # probably very this would be broken
    upload_input = upload.find_element_by_xpath("//input[@name='dash-uploader-upload']")
    upload_input.send_keys(str(testfile10Mb_csv))
    # Wait until file is uploaded

    upload_label = upload.find_element_by_xpath("//label")

    # Wait for "Completed" text, with 10 second timeout
    wait = WebDriverWait(dash_duo._driver, 10)
    wait.until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@id='dash-uploader']/*/label"), "Completed"
        )
    )

    # Get the div with the output values
    callback_output = dash_duo.find_element("#callback-output")

    # Get the name of the uploaded file
    uploaded_file = callback_output.find_element_by_xpath("//ul").text
    uploaded_file = Path(uploaded_file)

    assert uploaded_file.name == testfile10Mb_csv.name
    assert uploaded_file.exists()
    assert uploaded_file.stat().st_size == testfile10Mb_csv.stat().st_size

    # cleanup
    shutil.rmtree(uploaded_file.parent)
