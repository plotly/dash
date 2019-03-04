# Dash Core Components

This package provides the core React component suite for [Dash][].

[![CircleCI](https://circleci.com/gh/plotly/dash-core-components.svg?style=svg)](https://circleci.com/gh/plotly/dash-core-components)

## Development

### Testing Locally

1. Install the dependencies with:

```
$ npm i
```

2. Build the code:

```
$ npm run build
```

3. Install the library

```
$ python setup.py install
```

I recommend installing the library and running the examples in a fresh virtualenv in a separate folder:

```
$ mkdir dash_examples # create a new folder to test examples
$ cd dash_examples
$ virtualenv venv # create a virtual env
$ source venv/bin/activate # use the virtual env
```

(and then repeat step 3).

4. Add the following line to your Dash app
```
app.scripts.config.serve_locally = True
```

### Demo server

You can start up a demo development server to see a demo of the rendered
components:

```sh
$ npm start
```

You have to maintain the list of components in `demo/Demo.react.js`.

### Code quality and tests

### To run integration tests (test_integration.py)
You can run the Selenium integration tests with the
```sh
npm test
```
command, and the Jest unit tests with the
```sh
npm run test-unit
```

### Testing your components in Dash
1. Run the build watcher by running
        $ npm run build:watch

2. Run the dash layout you want to test

        # Import dash_core_components to your layout, then run it:
        $ python my_dash_layout.py

## Installing python package locally

You can run
        $ python setup.py install
to install the package locally, so you can test it out in your current environment.

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

[Dash]: https://plot.ly/dash
[Dash Component Boilerplate]: (https://github.com/plotly/dash-component-boilerplate)
[NPM package authors]: https://www.npmjs.com/package/dash-core-components/access
[PyPi]: https://pypi.python.org/pypi
