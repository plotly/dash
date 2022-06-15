# Dash Core Components

This package provides the core React component suite for [Dash][].

[![CircleCI](https://circleci.com/gh/plotly/dash-core-components.svg?style=svg)](https://circleci.com/gh/plotly/dash-core-components)

## Development

This package is part of `dash`, and if you install `dash` in development mode with extras as below, you can develop in this portion as well.
From the root of the `dash` repo:

```bash
# It's recommended to install your python packages in a virtualenv
# As of dash 2.0, python 3 is required
$ python -m venv venv && . venv/bin/activate

# make sure dash is installed with dev and testing dependencies
$ pip install -e .[dev,testing]  # in some shells you need \ to escape []

# run the build process - this will build all of dash, including dcc
$ npm ci && npm run build

# install dcc in editable mode
$ pip install -e .
```

### Code quality and tests

### To run integration tests (test_integration.py)
You can run the Selenium integration tests with the
```sh
npm test
```

### Testing your components in Dash
1. Run the build watcher by running
        $ npm run build:watch

2. Run the dash layout you want to test

        # Import dash_core_components to your layout, then run it:
        $ python my_dash_layout.py

## Dash Component Boilerplate

See the [dash-component-boilerplate](https://github.com/plotly/dash-component-boilerplate) repo for more information.

[Dash]: https://plotly.com/dash
[Dash Component Boilerplate]: (https://github.com/plotly/dash-component-boilerplate)
[NPM package authors]: https://www.npmjs.com/package/dash-core-components/access
[PyPi]: https://pypi.python.org/pypi


## Big Thanks
Cross-browser Testing Powered by [![image](https://user-images.githubusercontent.com/1394467/64290307-e4c66600-cf33-11e9-85a1-12c82230a597.png)](https://saucelabs.com)
