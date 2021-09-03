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
1. We recommend creating a virtual environment to install the requirements and run the examples. Create a virtual env with `virtualenv venv` and run with: `source venv/bin/activate`.
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
`npm run build`

## Local Dist Build
`python setup.py sdist`

Note: Distributable file will be located in ./dist

## Making a Contribution
_For larger features, your contribution will have a higher likelihood of getting merged if you create an issue to discuss the changes that you'd like to make before you create a pull request._

1. Create a pull request.
2. After a review has been done and your changes have been approved, they will be merged and included in a future release of Dash.

## [Checklists](http://rs.io/unreasonable-effectiveness-of-checklists/)
**Beginner tip:** _Copy and paste this section as a comment in your PR, then check off the boxes as you go!_
### Pre-Merge checklist
- [ ] All tests on CircleCI have passed.
- [ ] All visual regression differences have been approved.
- [ ] If changes are significant, a release candidate has been created and posted to Slack, the Plotly forums, and at the very top of the pull request.
- [ ] You have added an entry describing the change at the the top of `CHANGELOG.md`. For larger additions, your `CHANGELOG.md` entry includes sample code about how the feature works. The entry should also link to the original pull request(s).
- [ ] Two Dash core contributors have :dancer:'d the pull request.

### Post-Merge checklist
- [ ] You have deleted the branch.
- [ ] You have closed all issues that this pull request solves.
- [ ] If significant enough, you have created an issue about documenting the new feature or change and you have added it to the [dash-docs](https://github.com/plotly/dash-docs) project.

## Financial Contributions

Dash, and many of Plotly's open source products, have been funded through direct sponsorship by companies. [Get in touch][] about funding feature additions, consulting, or custom app development.

[GitHub flow]: https://guides.github.com/introduction/flow/
[semantic versioning]: https://semver.org/
[Dash Community Forum]: https://community.plotly.com/c/dash
[Get in touch]: https://plotly.com/products/consulting-and-oem
[Documentation]: https://github.com/orgs/plotly/projects/8
[Dash Docs]: https://github.com/plotly/dash-docs
