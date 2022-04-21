import time


def assert_clean_console(TestClass):
    def assert_no_console_errors(TestClass):
        TestClass.assertEqual(
            TestClass.driver.execute_script("return window.tests.console.error.length"),
            0,
        )

    def assert_no_console_warnings(TestClass):
        TestClass.assertEqual(
            TestClass.driver.execute_script("return window.tests.console.warn.length"),
            0,
        )

    assert_no_console_warnings(TestClass)
    assert_no_console_errors(TestClass)
