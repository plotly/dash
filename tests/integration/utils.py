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


def wait_for(condition_function, get_message=lambda: '', *args, **kwargs):
    """
    Waits for condition_function to return True or raises WaitForTimeout.
    :param (function) condition_function: Should return True on success.
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

    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
        del kwargs['timeout']
    else:
        timeout = TIMEOUT

    start_time = time.time()
    while time.time() < start_time + timeout:
        if wrapped_condition_function():
            return True
        time.sleep(0.5)

    raise WaitForTimeout(get_message())


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
