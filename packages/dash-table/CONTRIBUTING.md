# Contributing to Dash Table

## Getting Started
Refer to the [readme](README.md) for installation and basic use instructions.

## Coding Style
Please lint any Javascript / TypeScript additions with `npm run lint`.
Please lint any additions to Python code with `pylint` and `flake8`.

## Pull Request Guidelines
Use the [GitHub flow][] when
proposing contributions to this repository (i.e. create a feature branch and
submit a PR against the master branch).

## Developer Setup
1. Install Python 3.x (python 3 is required to run the demo apps and tests)
2. Install Node v8+
3. Install CircleCI CLI (https://circleci.com/docs/2.0/local-cli/)

`npm install`

## Local Demo
### Local Server JS Example (Hot reload)
Use to verify the frontend functionality of the table during development or initial testing. This will run the example in the `/demo` directory.

1. Run `npm run build.watch`
2. Visit [http://localhost:8080/](http://localhost:8080/)
### Local Server Review Apps
Use the review apps to verify callback functionality (note these examples are written in Python: the end-user syntax). This will run `index.py` found in the root of the directory and run the examples found in: `/tests/dash/`. To add more examples create a `.py` file in the `/tests/dash/` directory prepended with `app_` ie: `app_your_example.py`. This example will automatically get added to the example index page.
1. We recommend creating a virtual enviornment to install the requirements and run the examples. Create a virtual env with `virtualenv venv` and run with: `source venv/bin/activate`.
2. Run `pip install -r requirements.txt` from the root of the directory to install the requirements.
3. From the root of the directory run `gunicorn index:server`
4. Visit [http://127.0.0.1:8000](http://localhost:8000)

## Running Tests
### Run tests locally
`npm test`
### Run tests locally with hot reload:
`npm run test.watch`
### Run tests in CircleCI CLI
`circleci build --job test`

## Local Build
`npm run build:js && npm run build:py`

## Local Dist Build
`python setup.py sdist`

Note: Distributable file will be located in ./dist

## Making a Contribution
_For larger features, your contribution will have a higher likelihood of getting merged if you create an issue to discuss the changes that you'd like to make before you create a pull request._

1. Create a pull request and tag the Plotly team (`@plotly/dash`) and tag / request review from [@Marc-Andre-Rivet](https://github.com/Marc-Andre-Rivet) and [@valentijnnieman ](https://github.com/valentijnnieman).
2. After a review has been done and your changes have been approved, create a prerelease and comment in the PR. Version numbers should follow [semantic versioning][]. To create a prerelease:
    * Add `-rc1` to `package.json` e.g. `0.14.0-rc1`
    * Run `npm publish`.
    * Upload your release to pypi with: `twine upload dist/dash_table-X.X.X.tar.gz`
        - If needed, ask @chriddyp to get NPM / PyPi package publishing access.
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
- [ ] You have updated the version and the top of `CHANGELOG.md`. For larger additions, your `CHANGELOG.md` entry includes sample code about how the feature works. The entry should also link to the original pull request(s).
- [ ] Two Dash core contributors have :dancer:'d the pull request.

### Post-Merge checklist
- [ ] You have tagged the release using `git tag v<version_number>` _(for the contributor merging the PR)_.
- [ ] You have pushed this tag using `git push <tag_name>` _(for the contributor merging the PR)_.
- [ ] You have deleted the branch.

### Pre-Release checklist
- [ ] Everything in the Pre-Merge checklist is completed. (Except the last two if this is a release candidate).
- [ ] `git remote show origin` shows you are in the correct repository.
- [ ] `git branch` shows that you are on the expected branch.
- [ ] `git status` shows that there are no unexpected changes.

### Release Step
- `python setup.py sdist` to build.
- `twine upload dist/<the_version_you_just_built>` to upload to PyPi.

### Post-Release checklist
- [ ] You have closed all issues that this pull request solves, and commented the new version number users should install.
- [ ] If significant enough, you have created an issue about documenting the new feature or change and you have added it to the [Documentation][] project.
- [ ] You have created a pull request in [Dash Docs][] with the new release of your feature by editing that project's [`requirements.txt` file](https://github.com/plotly/dash-docs/blob/master/requirements.txt) and you have assigned `@chriddyp` or `@cldougl` to review.

## Financial Contributions

Dash, and many of Plotly's open source products, have been funded through direct sponsorship by companies. [Get in touch][] about funding feature additions, consulting, or custom app development.

[GitHub flow]: https://guides.github.com/introduction/flow/
[semantic versioning]: https://semver.org/
[Dash Community Forum]: https://community.plot.ly/c/dash
[Get in touch]: https://plot.ly/products/consulting-and-oem
[Documentation]: https://github.com/orgs/plotly/projects/8
[Dash Docs]: https://github.com/plotly/dash-docs
