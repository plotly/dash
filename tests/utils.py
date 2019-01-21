import time


TIMEOUT = 5  # Seconds


def invincible(func):
    def wrap():
        try:
            return func()
        except:
            pass
    return wrap


class WaitForTimeout(Exception):
    """This should only be raised inside the `wait_for` function."""
    pass


def wait_for(condition_function, get_message=None, expected_value=None,
             timeout=TIMEOUT, *args, **kwargs):
    """
    Waits for condition_function to return truthy or raises WaitForTimeout.
    :param (function) condition_function: Should return truthy or
        expected_value on success.
    :param (function) get_message: Optional failure message function
    :param expected_value: Optional return value to wait for. If omitted,
        success is any truthy value.
    :param (float) timeout: max seconds to wait. Defaults to 5
    :param args: Optional args to pass to condition_function.
    :param kwargs: Optional kwargs to pass to condition_function.
        if `timeout` is in kwargs, it will be used to override TIMEOUT
    :raises: WaitForTimeout If condition_function doesn't return True in time.
    Usage:
        def get_element(selector):
            # some code to get some element or return a `False`-y value.
        selector = '.js-plotly-plot'
        try:
            wait_for(get_element, selector)
        except WaitForTimeout:
            self.fail('element never appeared...')
        plot = get_element(selector)  # we know it exists.
    """
    def wrapped_condition_function():
        """We wrap this to alter the call base on the closure."""
        if args and kwargs:
            return condition_function(*args, **kwargs)
        if args:
            return condition_function(*args)
        if kwargs:
            return condition_function(**kwargs)
        return condition_function()

    start_time = time.time()
    while time.time() < start_time + timeout:
        condition_val = wrapped_condition_function()
        if expected_value is None:
            if condition_val:
                return True
        elif condition_val == expected_value:
            return True
        time.sleep(0.5)

    if get_message:
        message = get_message()
    elif expected_value:
        message = 'Final value: {}'.format(condition_val)
    else:
        message = ''

    raise WaitForTimeout(message)


def assert_clean_console(TestClass):
    def assert_no_console_errors(TestClass):
        TestClass.assertEqual(
            TestClass.driver.execute_script(
                'return window.tests.console.error.length'
            ),
            0
        )

    def assert_no_console_warnings(TestClass):
        TestClass.assertEqual(
            TestClass.driver.execute_script(
                'return window.tests.console.warn.length'
            ),
            0
        )

    assert_no_console_warnings(TestClass)
    assert_no_console_errors(TestClass)
