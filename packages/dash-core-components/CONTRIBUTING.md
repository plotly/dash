## Running the Tests

In order to run the tests, you first need to have built the JavaScript
`dash_core_components` library. You will need to build the library again if
you've pulled from upstream otherwise you may be running with an out of data
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
