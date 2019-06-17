# Contributing to dash-core-components

## Getting Started

Refer to the [readme](README.md) for installation and development instructions.

## Contributions

[Dash Core Components][] consist of pluggable components for creating interactive user interfaces. For generic HTML5 elements, see [Dash HTML Components][]. Contributions are welcome! This repository's open [issues][] are a good place to start. Another way to contribute is to [write your own components][] using the [Dash Components Archetype][].

## Coding Style

Please lint any additions to react components with `npm run lint`. Rules defined in [.eslintrc](.eslintrc) are inherited from [`dash-components-archetype`](https://github.com/plotly/dash-components-archetype)'s [eslintrc-react.json][]

## Pull Request Guidelines

Use the [GitHub flow][] when proposing contributions to this repository (i.e. create a feature branch and submit a PR against the master branch).

## Running the Tests

In order to run the tests, you first need to have built the JavaScript
`dash_core_components` library. You will need to build the library again if
you've pulled from upstream otherwise you may be running with an out of date
`bundle.js`. See the instructions for building `bundle.js` in the [Testing
Locally](README.md#testing-locally) section of README.md.

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

## Publishing New Components/Features

For now, multiple steps are necessary for publishing to NPM and PyPi,
respectively. TODO:
[#5](https://github.com/plotly/dash-components-archetype/issues/5) will roll up publishing steps into one workflow.

1. Create a pull request and tag the Plotly team (`@plotly/dash`) as well as an appropriate reviewer (frequent [contributors][] are a safe bet).
2. After a review has been done and your changes have been approved, create a prerelease and comment in the PR. Version numbers should follow [semantic versioning][]. To create a prerelease:
    * Add `rc1` to `version.py` (`./dash_core_components/version.py`) e.g. `0.13.0rc1`
    * Add `-rc1` to `package.json` e.g. `0.13.0-rc1`
    * Update the `unpkg` link in `./dash_core_components/__init__.py`, replacing `__version__` with your release candidate (e.g. `"0.13.0-rc1"`)
    * Run `npm run publish-all`.
        - If needed, ask @chriddyp to get NPM / PyPi package publishing access.
        - If the `publish-all` script fails on the `twine` command, try running
            ```sh
            twine upload dist/dash_core_components-X.X.X.tar.gz # where xx.x.x is the version number
            ```
3. Comment in the PR with the prerelease version
4. Update the top-level comment to include info about how to install, a summary of the changes, and a simple example. For a good example, see the [Confirmation Modal component][].
    * This makes it easier for a community member to come in and try it out. As more folks review, it's harder to find the installation instructions deep in the PR
    * Keep this top-level comment updated with installation instructions (e.g. the `pip install` command)
5. Make a post in the [Dash Community Forum][]
    * Title it `":mega: Announcement! New <Your Feature> - Feedback Welcome"`
    * In the description, link to the PR and any relevant issue(s)
    * Pin the topic so that it appears at the top of the forum for two weeks
    * For a good example, see the [Confirmation Modal announcement][]

## Updating Plotly.js

1. Download the latest plotly.js from the cdn: `$ wget https://github.com/plotly/plotly.js/releases/tag/v1.48.3`
2. Update `dash_core_components/__init__.py` plotly.js `external_url`
3. Update `CHANGELOG.md` with links to the releases and a description of the changes. The message should state (see the existing `CHANGELOG.md` for examples):
    * If you're only bumping the patch level, the heading is "Fixed" and the text starts "Patched plotly.js". Otherwise the heading is "Updated" and the text starts "Upgraded plotly.js"
    * The new plotly.js version number, and the PR in which this was done
    * All major or minor versions included, with links to their release pages and a summary of the major new features in each. If there are multiple minor/major releases included, be sure to look at all of their release notes to construct the summary. Call minor versions "feature" versions for the benefit of users not steeped in semver terminology.
    * All patch versions included, with links to their release pages and a note that these fix bugs
4. When bumping the dcc version, a plotly.js patch/minor/major constitutes a dcc patch/minor/major respectively as well.

## Financial Contributions

If your company wishes to sponsor development of open source dash components, please [get in touch][].

[Dash Core Components]: https://dash.plot.ly/dash-core-components
[Dash HTML Components]: https://github.com/plotly/dash-html-components
[write your own components]: https://dash.plot.ly/plugins
[Dash Components Archetype]: https://github.com/plotly/dash-components-archetype
[issues]: https://github.com/plotly/dash-core-components/issues
[GitHub flow]: https://guides.github.com/introduction/flow/
[eslintrc-react.json]: https://github.com/plotly/dash-components-archetype/blob/master/config/eslint/eslintrc-react.json
[contributors]: https://github.com/plotly/dash-core-components/graphs/contributors
[semantic versioning]: https://semver.org/
[Dash Community Forum]: https://community.plot.ly/c/dash
[Confirmation Modal component]: https://github.com/plotly/dash-core-components/pull/211#issue-195280462
[Confirmation Modal announcement]: https://community.plot.ly/t/announcing-dash-confirmation-modal-feedback-welcome/11627
[get in touch]: https://plot.ly/products/consulting-and-oem
