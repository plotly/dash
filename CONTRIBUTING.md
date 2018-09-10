# Contributing to dash

## Getting Started

Refer to the [readme](README.md) for installation and development instructions.

## Coding Style

Please lint any additions to react components with `pylint` and `flake8`.

## Pull Request Guidelines

Use the [GitHub flow][] when proposing contributions to this repository (i.e. create a feature branch and submit a PR against the master branch).

## Running the Tests

To run the tests, you can use Python's `unittest` module, or a test runner like `nose2`.

To run all of the tests:
`python -m unittest tests`

Or:
`nose2 -v`

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

## Making a contribution

1. Create a pull request and tag the Plotly team (`@plotly/dash`) as well as an appropriate reviewer (frequent [contributors][] are a safe bet).
2. After a review has been done and your changes have been approved, create a prerelease and comment in the PR. Version numbers should follow [semantic versioning][]. To create a prerelease:
    * Add `rc1` to `version.py` (`./dash/version.py`) e.g. `0.13.0rc1`
        - If needed, ask @chriddyp to get PyPi package publishing access.
    * Run `python setup.py sdist` to build a distribution zip.
    * Check the `dist` folder for a zip ending with your selected version number. Double check that this version number ends with `rc#`, as to not mistakenly publish the package.
    * Run `twine upload dist/<package_name>`.
3. Comment in the PR with the prerelease version
4. Update the top-level comment to include info about how to install, a summary of the changes, and a simple example.
    * This makes it easier for a community member to come in and try it out. As more folks review, it's harder to find the installation instructions deep in the PR
    * Keep this top-level comment updated with installation instructions (e.g. the `pip install` command)
5. Make a post in the [Dash Community Forum][]
    * Title it `":mega: Announcement! New <Your Feature> - Feedback Welcome"`
    * In the description, link to the PR and any relevant issue(s)
    * Pin the topic so that it appears at the top of the forum for two weeks

## [Checklists](http://rs.io/unreasonable-effectiveness-of-checklists/)
### Pre-Merge checklist
- [ ] All tests on CircleCI have passed.
- [ ] All visual regression differences have been approved.
- [ ] If changes are significant, a release candidate has been created and posted to Slack, the Plotly forums, and at the very top of the pull request.
- [ ] You have updated the `dash/version.py` file and the top of `CHANGELOG.md`
- [ ] Two people have :dancer:'d the pull request. You can be one of these people if you are a Dash core contributor.

### Pre-Release checklist
- [ ] Everything in the Pre-Merge checklist is completed. (Except the last one if this is a release candidate).
- [ ] `git remote show origin` shows you are in the correct repository.
- [ ] `git branch` shows that you are on the expected branch.
- [ ] `git status` shows that there are no unexpected changes.
- [ ] `dash/version.py` is at the correct version.
- [ ] You have tagged the release using `git tag v<version_number`.

## Financial Contributions

If your company wishes to sponsor development of open source dash components, please [get in touch][].

[Dash Core Components]: https://dash.plot.ly/dash-core-components
[Dash HTML Components]: https://github.com/plotly/dash-html-components
[write your own components]: https://dash.plot.ly/plugins
[Dash Component Biolerplate]: https://github.com/plotly/dash-component-boilerplate
[issues]: https://github.com/plotly/dash-core-components/issues 
[GitHub flow]: https://guides.github.com/introduction/flow/
[eslintrc-react.json]: https://github.com/plotly/dash-components-archetype/blob/master/config/eslint/eslintrc-react.json
[contributors]: https://github.com/plotly/dash-core-components/graphs/contributors
[semantic versioning]: https://semver.org/
[Dash Community Forum]: https://community.plot.ly/c/dash
[Confirmation Modal component]: https://github.com/plotly/dash-core-components/pull/211#issue-195280462
[Confirmation Modal announcement]: https://community.plot.ly/t/announcing-dash-confirmation-modal-feedback-welcome/11627
[get in touch]: https://plot.ly/products/consulting-and-oem
