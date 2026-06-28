"""Test: disabled
The test file used for checking the following properties:
   - disabled
   - disableDragAndDrop
"""
import json
from pathlib import Path
import shutil

import chromedriver_binary  # noqa: F401
from dash.testing.application_runners import import_app
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

from .utils import create_file, load_text_file

# NOTE: Here are some notes for testing
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


@pytest.fixture
def testfileWrongType():
    file = Path(__file__).resolve().parent / "mytestfile.wrong"
    create_file(file, filesize_mb=1)
    yield file
    file.unlink()


@pytest.fixture
def js_drag_and_drop():
    """Provide file drag and drop simulation.
    selenium only supports drag and drop elements.
    The javascript used for triggering a drag and drop file operation.
    Thanks for the work:
        https://gist.github.com/florentbr/349b1ab024ca9f3de56e6bf8af2ac69e
    Used as:
        driver.execute_script(js_drag_and_drop, #1, #2, #3)

    Parameters:
    ----------
    #1 The element with the drag and drop area.
    #2 Drop offset x relative to the top/left corner of the drop area. Center if 0.
    #3 Drop offset y relative to the top/left corner of the drop area. Center if 0.

    Returns:
    -------
    A file <input> element used for simulating drag and drop.
    """
    return load_text_file(
        file_path=Path(__file__).resolve().parent / "js" / "drag_and_drop_simulation.js"
    )


# Basic test for the "disabled" property.
# Run with pytest -k disabled01
def test_disabled01_check_disabled_property_update(dash_duo):
    """Check the update of the disabled property.
    The trigger of "disabled" would make the class of the upload component change.
    """
    # Fetch the test app.
    app = import_app("tests.apps.disabled")
    dash_duo.start_server(app)
    wait = WebDriverWait(dash_duo._driver, 10)

    # Find the required components
    upload = dash_duo.find_element("#dash-uploader")
    configs = dash_duo.find_element("#uploader-configs")
    check_boxes = configs.find_elements_by_xpath(".//input[@type='checkbox']")
    assert len(check_boxes) == 2, "The provided configs for this app should be 2."

    # Check the upload state, should be default now.
    assert (
        upload.get_attribute("class") == "dash-uploader-default"
    ), 'The current uploader class should be "dash-uploader-default".'

    # Click the checkbox named "Disabled".
    check_boxes[0].click()

    # Wait for "configs-output" updated, with 10 second timeout.
    wait.until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//span[@id='configs-output']"), json.dumps([0,])
        )
    )

    # Check the upload state, should be disabled now.
    assert (
        upload.get_attribute("class") == "dash-uploader-disabled"
    ), 'The current uploader class should be "dash-uploader-disabled".'

    # Click the checkbox named "Disabled" again.
    check_boxes[0].click()

    # Wait for "configs-output" updated, with 10 second timeout.
    wait.until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//span[@id='configs-output']"), json.dumps([])
        )
    )

    # Check the upload state, should be disabled now.
    assert (
        upload.get_attribute("class") == "dash-uploader-default"
    ), 'The current uploader class should be "dash-uploader-default".'


def test_disabled02_check_disabled_effect(
    dash_duo, testfile10Mb_csv, testfileWrongType, js_drag_and_drop
):
    """Check the effectiveness of the disabled and disableDragAndDrop property.
    The upload component with "disabled" triggered would not accept any files.
    The upload component with "disableDragAndDrop" would not accept files uploaded by drag and drop region.
    """
    # Fetch the test app.
    app = import_app("tests.apps.disabled")
    dash_duo.start_server(app)
    driver = dash_duo._driver
    wait = WebDriverWait(driver, 10)

    # Find the required components
    upload = dash_duo.find_element("#dash-uploader")
    configs = dash_duo.find_element("#uploader-configs")
    check_boxes = configs.find_elements_by_xpath(".//input[@type='checkbox']")
    assert len(check_boxes) == 2, "The provided configs for this app should be 2."

    # Define the upload check function.
    def upload_test_file_and_validate(
        upload_component, is_disabled=False, by_dragndrop=False, expect_success=True
    ):
        """Upload a file and check the results.
        If "expect_success" is True, the file is expected to be uploaded;
        If not, the uploading is expected to fail.
        """
        upload_input = upload_component.find_element_by_xpath(
            ".//input[@name='dash-uploader-upload']"
        )
        # First, upload a wrong file. This would reset the message of upload component.
        upload_input.send_keys(str(testfileWrongType))

        if (
            not is_disabled
        ):  # Skip this step if the component is disabled, because the message would no be changed now.
            # Wait until the text is reset.
            wait.until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, "//div[@id='dash-uploader']/*/label"), "Invalid"
                )
            )

        if by_dragndrop:
            # Create a file_input, which simulates the drag and drop behavior.
            # This <input> element is different from the input element created by dash uploader.
            drag_and_drag_input = driver.execute_script(
                js_drag_and_drop, upload, 20, 20
            )
            drag_and_drag_input.send_keys(str(testfile10Mb_csv))
        else:
            # Ensure the uploading button is clickable.
            if expect_success:
                assert (
                    upload_input.is_enabled()
                ), "The uploading button is expected to be enabled."
            else:  # This step is expected to fail when "expect_success=False"
                # The err_info is used for showing the message.
                with pytest.raises(AssertionError) as err_info:  # noqa: F841
                    assert (
                        upload_input.is_enabled()
                    ), "The uploading button is expected to be enabled."
                return

            # Wait until file is uploaded
            upload_input.send_keys(str(testfile10Mb_csv))

        # The fail case would be used for checking the drag and drop mode.
        if expect_success:
            wait.until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, "//div[@id='dash-uploader']/*/label"), "Completed"
                )
            )
        else:
            # The err_info is used for showing the message.
            with pytest.raises(TimeoutException) as err_info:  # noqa: F841
                wait.until(
                    EC.text_to_be_present_in_element(
                        (By.XPATH, "//div[@id='dash-uploader']/*/label"), "Completed"
                    )
                )
            return

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

    # Check the upload state, should be default or complelte now.
    uploader_class = upload.get_attribute("class")
    assert (
        uploader_class == "dash-uploader-default"
        or uploader_class == "dash-uploader-complete"
    ), 'The current uploader class should be "dash-uploader-default" or "dash-uploader-complete".'

    # Upload the file, both tests are expected to sucess.
    upload_test_file_and_validate(
        upload, by_dragndrop=False, expect_success=True
    )  # By sending the file.
    upload_test_file_and_validate(
        upload, by_dragndrop=True, expect_success=True
    )  # By drag and drop.

    # Check the performance of the disabled case.
    check_boxes[0].click()

    # Wait for the component update getting confirmed.
    wait.until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//span[@id='configs-output']"), json.dumps([0,])
        )
    )

    # Check the upload state, should be disabled now.
    assert (
        upload.get_attribute("class") == "dash-uploader-disabled"
    ), 'The current uploader class should be "dash-uploader-disabled".'

    # Upload the file, both tests are expected to fail.
    upload_test_file_and_validate(
        upload, is_disabled=True, by_dragndrop=False, expect_success=False
    )  # By sending the file.
    upload_test_file_and_validate(
        upload, is_disabled=True, by_dragndrop=True, expect_success=False
    )  # By drag and drop.

    # Check the performance of the disableDragAndDrop case.
    check_boxes[0].click()
    check_boxes[1].click()

    # Wait for the component update getting confirmed.
    wait.until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//span[@id='configs-output']"), json.dumps([1,])
        )
    )

    # Check the upload state, should be default or complelte now.
    uploader_class = upload.get_attribute("class")
    assert (
        uploader_class == "dash-uploader-default"
        or uploader_class == "dash-uploader-complete"
    ), 'The current uploader class should be "dash-uploader-default" or "dash-uploader-complete".'

    # Upload the file, the normal test is expected to success, while the drag and drop test is expected to fail.
    upload_test_file_and_validate(
        upload, by_dragndrop=False, expect_success=True
    )  # By sending the file.
    upload_test_file_and_validate(
        upload, by_dragndrop=True, expect_success=False
    )  # By drag and drop.
