## Running the Tests

In order to run the tests, you first need to have built the JavaScript
`dash_core_components` library. You will need to build the library again if
you've pulled from upstream otherwise you may be running with an out of date
`bundle.js`. See the instructions for building `bundle.js` in the "Testing
Locally" section of README.md.

You also need to set the environment variable `TOX_PYTHON_27` and with the
location of the Python 2 installations you want tox to use for creating the
virtualenv that will be used to run the tests. Note that this means you do not
need to install any dependencies into the installation yourself.

If you're using pyenv to manage Python installations, you would do something
like this:

```
export TOX_PYTHON_27=~/.pyenv/versions/2.7.14/bin/python
```

## Local configuration
You can configure the test server with the following variables:
### DASH_TEST_CHROMEPATH
If you run a special chrome set the path to your chrome binary with this environment variable.

### DASH_TEST_PROCESSES
If you encounter errors about Multi-server + Multi-processing when running under Python 3 try running the tests with the number of server processes set to 1.

### Example: single test run with configuration
```
DASH_TEST_CHROMEPATH=/bin/google-chrome-beta DASH_TEST_PROCESSES=1 python -m unittest -v test.test_integration.Tests.test_inputs
```
