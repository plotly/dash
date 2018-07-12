# Dash Core Components

This package provides the core React component suite for [Dash][].

[![CircleCI](https://circleci.com/gh/plotly/dash-core-components.svg?style=svg)](https://circleci.com/gh/plotly/dash-core-components)
[![Greenkeeper badge](https://badges.greenkeeper.io/plotly/dash-core-components.svg)](https://greenkeeper.io/)

## Development

### Testing Locally

1. Install the dependencies with:

```
$ npm i
```

2. Build the code:

```
$ npm run build-dev
```

3. Install the library

```
$ cd dash-core-components
$ npm run copy-lib
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
$ builder run demo
$ open http://localhost:9000
```

You have to maintain the list of components in `demo/Demo.react.js`.

### Code quality and tests

### To run integration tests (test_integration.py)
We run our integration tests on CircleCI with help from Tox. There’s a tox.ini file which holds the configuration, refer to [tox's documentation](http://tox.readthedocs.io/en/latest/index.html) for help. You may need to set environment variables in your terminal, like `TOX_PYTHON_27` to my version of python that I wanted tox to use. So running:

```sh
export TOX_PYTHON_27=python2
```

set the `TOX_PYTHON_27` env variable to point to `python2`, which is Python 2.7 running on my machine. 
You could also look in `tox.ini` and see which tests it runs, and run those commands yourself: 

```sh
python -m unittest test.test_integration
```

### Testing your components in Dash

1. Build development bundle to `lib/` and watch for changes

        # Once this is started, you can just leave it running.
        $ npm start

2. Install module locally (after every change)

        # Generate metadata, and build the JavaScript bundle
        $ npm run install-local

        # Now you're done. For subsequent changes, if you've got `npm start`
        # running in a separate process, it's enough to just do:
        $ python setup.py install

3. Run the dash layout you want to test

        # Import dash_core_components to your layout, then run it:
        $ python my_dash_layout.py

## Installing python package locally

Before publishing to PyPi, you can test installing the module locally:

```sh
# Install in `site-packages` on your machine
$ npm run install-local
```

## Uninstalling python package locally

```sh
$ npm run uninstall-local
```

## Publishing

For now, multiple steps are necessary for publishing to NPM and PyPi,
respectively. TODO:
[#5](https://github.com/plotly/dash-components-archetype/issues/5) will roll up
publishing steps into one workflow.

Ask @chriddyp to get NPM / PyPi package publishing access.

1 - Update `version.py`, we're using [semantic versioning](https://semver.org/)!

2 - Update `package.json`

4 - Publish: `npm run publish-all` (Make sure you have access to NPM and PyPI)
4b - If the `publish-all` script fails on the `twine` command, try running
```sh
twine upload dist/dash_core_components-X.X.X.tar.gz # where xx.x.x is the version number
```

If you want to publish a prerelease package, change `version.py` to X.X.XrcX (0.23.1rc1 for example) and
`package.json` to X.X.X-rcX (notice how the rc syntax is different between node and python. npm requires a - between the version number and the prerelease tag while python's pip just has 0.23.1rc1)


## Builder / Archetype

We use [Builder][] to centrally manage build configuration, dependencies, and
scripts.

To see all `builder` scripts available:

```sh
$ builder help
```

See the [dash-components-archetype][] repo for more information.

[Builder]: https://github.com/FormidableLabs/builder
[Dash]: https://plot.ly/dash
[NPM package authors]: https://www.npmjs.com/package/dash-core-components/access
[PyPi]: https://pypi.python.org/pypi
[dash-components-archetype]: https://github.com/plotly/dash-components-archetype
