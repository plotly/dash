# Contributing to dash

## Getting Started

Fork and clone the dash [repo](https://github.com/plotly/dash).

To set up your development environment, run the following commands:
```bash
# Move into the clone
$ cd dash
# Create a virtualenv
$ python3 -m venv venv
# Activate the virtualenv
$ . venv/bin/activate
# (On Windows, the above would be: venv\scripts\activate)
# Install the dev dependencies
$ pip install -r .circleci/requirements/dev-requirements.txt
```

## Coding Style

Please lint any additions to Python code with `pylint` and `flake8`.

## Pull Request Guidelines

Use the [GitHub flow][] when proposing contributions to this repository (i.e. create a feature branch and submit a PR against the master branch).

## Running the Tests

**Warning:** _Tests do not currently run on Windows. Track our progress: [#409](https://github.com/plotly/dash/issues/409)._

To run the tests, you can use Python's `unittest` module, or a test runner like `nose2`.
For example, `python -m unittest tests.test_integration` will run the integration tests.

To run all of the tests:
`python -m unittest discover tests`

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
_For larger features, your contribution will have a higher likelihood of getting merged if you create an issue to discuss the changes that you'd like to make before you create a pull request._

1. Create a pull request and tag the Plotly team (`@plotly/dash`) and tag / request review from [@rmarren1](https://github.com/rmarren1) and [@T4rk1n](https://github.com/T4rk1n).
2. After a review has been done and your changes have been approved, create a prerelease and comment in the PR. Version numbers should follow [semantic versioning][]. To create a prerelease:
    * Add `rc1` to `version.py` (`./dash/version.py`) e.g. `0.13.0rc1`
        - If needed, ask @chriddyp to get PyPi package publishing access.
    * Run `python setup.py sdist` to build a distribution zip.
    * Check the `dist` folder for a `tar.gz` file ending with your selected version number. Double check that this version number ends with `rc#`, as to not mistakenly publish the package.
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
**Beginner tip:** _Copy and paste this section as a comment in your PR, then check off the boxes as you go!_
### Pre-Merge checklist
- [ ] All tests on CircleCI have passed.
- [ ] All visual regression differences have been approved.
- [ ] If changes are significant, a release candidate has been created and posted to Slack, the Plotly forums, and at the very top of the pull request.
- [ ] You have updated the `dash/version.py` file and the top of `CHANGELOG.md`. For larger additions, your `CHANGELOG.md` entry includes sample code about how the feature works. The entry should also link to the original pull request(s).
- [ ] Two people have :dancer:'d the pull request. You can be one of these people if you are a Dash core contributor.

### Post-Merge checklist
- [ ] You have tagged the release using `git tag v<version_number>` _(for the contributor merging the PR)_.
- [ ] You have pushed this tag using `git push <tag_name>` _(for the contributor merging the PR)_.
- [ ] You have deleted the branch.

### Pre-Release checklist
- [ ] Everything in the Pre-Merge checklist is completed. (Except the last two if this is a release candidate).
- [ ] `git remote show origin` shows you are in the correct repository.
- [ ] `git branch` shows that you are on the expected branch.
- [ ] `git status` shows that there are no unexpected changes.
- [ ] `dash/version.py` is at the correct version.

### Release Step
- `python setup.py sdist` to build.
- `twine upload dist/<the_version_you_just_built>` to upload to PyPi.

### Post-Release checklist
- [ ] You have closed all issues that this pull request solves, and commented the new version number users should install.
- [ ] If significant enough, you have created an issue about documenting the new feature or change and you have added it to the [Documentation] project.
- [ ] You have created a pull request in [Dash Docs] with the new release of your feature by editing that project's [`requirements.txt` file](https://github.com/plotly/dash-docs/blob/master/requirements.txt) and you have assigned `@chriddyp` to review.

## Versioning Policy
This repository adheres to [semver](https://semver.org/). The following policy is in effect for `dash`, `dash-core-components`, `dash-html-components` and `dash-renderer`:
1. Matching major version numbers are guarenteed to work together.
2. Any change to the public API (breaking change) will increase a major version.

1 and 2 imply that when any core `dash*` repo introduces a breaking change all `dash*` repos will increment their major versions to match. This process is called a **major release candidate window** and is outlined below.

### Major Release Candidate Window
1. The major release candidate window will be announced internally at Plotly and through our popular community channels.
2. `dash`, `dash-core-components`, `dash-html-components` and `dash-renderer` master branches will be reversioned as `N.0.0-rc1` on the same day and published for testing.
3. Pull requests especially those containing breaking changes will be merged.
4. Per repo tests will be updated to target the latest `rc` versions.
5. [dash-docs](https://github.com/plotly/dash-docs), some apps in the [dash gallery](https://dash.plot.ly/gallery) and Plotly internal projects will be updated to target the latest `rc` versions.
6. steps 3-5 will continue until all breaking changes have been merged.
7. A major release candidate freeze will go into effect. During this time steps 3-5 will continue but only bug fixes will be merged.
8. Once testing and Q/A is complete `dash`, `dash-core-components`, `dash-html-components` and `dash-renderer` master branches will be reversioned as `N.0.0` and published ending the major release candidate window.

### Backporting fixes
During and after the major release candidate window bug fixes that can apply to pre-major release candidate releases should be backported. This is accomplished by:
1. If a pre-major release branch does not exist then check out a branch at the tag defining the last published release before the previous major release candidate window began. For example if we are in the `1.x` series and the last pre-`1.x` series release is `v0.18.1` checkout a branch at `v0.18.1` called `0.18-release`. If the branch does exist check it out.
2. Cherry-pick or otherwise reapply the fix to the pre-major release branch and update the patch version. In the example above the new version and tag will be `v0.18.2` on the `0.18-release` branch.
3. Publish.

## Financial Contributions

Dash, and many of Plotly's open source products, have been funded through direct sponsorship by companies. [Get in touch] about funding feature additions, consulting, or custom app development.

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
[Get in touch]: https://plot.ly/products/consulting-and-oem
[Documentation]: https://github.com/orgs/plotly/projects/8
[Dash Docs]: https://github.com/plotly/dash-docs
