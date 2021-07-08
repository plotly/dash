# Dash Core Components

This package provides the core React component suite for [Dash][].

[![CircleCI](https://circleci.com/gh/plotly/dash-core-components.svg?style=svg)](https://circleci.com/gh/plotly/dash-core-components)

## Development

The `dash` package contains some tools to build components and drive the bundles build process.
To avoid the circular dependency situation, we don't add `dash` as a required install in the `dash-core-components` setup.
But, in order to do development locally, you need to install `dash` before everything.

1. Install the dependencies with:

```bash
# it's recommended to install your python packages in a virtualenv
# python 2
$ pip install virtualenv --user && virtualenv venv && . venv/bin/activate
# python 3
$ python -m venv venv && . venv/bin/activate

# make sure dash is installed with dev and testing dependencies
$ pip install dash[dev,testing]  # in some shells you need \ to escape []

# run the build process
$ npm i --ignore-scripts && npm run build

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

## Uninstalling python package locally

```sh
$ npm run uninstall-local
```

## Publishing

There's an npm script that will handle publish, provided you have the right credentials. You can run it by running

```sh
$ npm run publish-all
```

See the [Publishing New Components/Features](CONTRIBUTING.md#publishing-new-componentsfeatures) section of the Contributing guide for step-by-step instructions on publishing new components.

## Dash Component Boilerplate

See the [dash-component-boilerplate](https://github.com/plotly/dash-component-boilerplate) repo for more information.

[Dash]: https://plotly.com/dash
[Dash Component Boilerplate]: (https://github.com/plotly/dash-component-boilerplate)
[NPM package authors]: https://www.npmjs.com/package/dash-core-components/access
[PyPi]: https://pypi.python.org/pypi


## Big Thanks
Cross-browser Testing Powered by [![image](https://user-images.githubusercontent.com/1394467/64290307-e4c66600-cf33-11e9-85a1-12c82230a597.png)](https://saucelabs.com)
