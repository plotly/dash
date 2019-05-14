# Contributor Guide

## Getting Started

Glad that you decided to make your contribution in Dash, to set up your development environment, run the following commands:

```bash
# in your working directory
$ git clone https://github.com/plotly/dash
$ cd dash
# create a virtualenv
$ python3 -m venv venv
# activate the virtualenv (on windows venv\scripts\activate)
$ . venv/bin/activate
# Install the dev dependencies
$ pip install -r .circleci/requirements/dev-requirements.txt
```
## Git

Use the [GitHub flow][] when proposing contributions to this repository (i.e. create a feature branch and submit a PR against the **dev** branch).

### Organize your commits

For pull request with notable file changes or a big feature developmennt, we highly recommend to organize the commits in a logical manner, so it

- makes a code review experience much more pleasant
- facilitates a possible cherry picking with granular commits

*an intutive [example](https://github.com/plotly/dash-core-components/pull/548) is worth a thousand words.*

#### Git Desktop

Git command veterans might argue that a simple terminal and cherry switch powered keyboard is the most elegant solution. But in general, a desktop tool makes the task easier.

1. https://www.gitkraken.com/git-client
2. https://desktop.github.com/

### Emoji

Plotlyers love to use emoji as an effective communication medium for

**Commit Messages**

Emojis make the commit messages :cherry_blossom:. If you have no idea about what to add ? Here is a nice [cheatsheet](https://gitmoji.carloscuesta.me/) and just be creative!

**Code Review Comments**

- :dancer: `:dancer:` - used to indicate you can merge!  Equivalent to GitHub's :squirrel:
- :cow2: `:cow2:` cow tip - minor coding style or code flow point
- :tiger2: `:tiger2:` testing tiger - something needs more tests, or tests need to be improved
- :snake: `:snake:` security snake - known or suspected security flaw
- :goat: `:goat:` grammar goat
- :smile_cat: `:smile_cat:` happy cat - for bits of code that you really like!
- :dolls: `:dolls:` documentation dolls
- :pill: `:pill:` performance enhancing pill
- :hocho: `:hocho:` removal of large chunks of code (obsolete stuff, or feature removals)
- :bug: `:bug:` - a bug of some kind. 8 legged or 6. Sometimes poisonous.
- :camel: :palm_tree: `:camel:` `:palm_tree:` - The Don't Repeat Yourself (DRY) camel or palm tree.
- :space_invader: `:space_invader:` - Too much space or too little.
- :spaghetti: `:spaghetti:` - copy-pasta, used to signal code that was copy-pasted without being updated

## Testing before your first push

You can use [circleci local cli](https://circleci.com/docs/2.0/local-cli/) to **locally** test your branch before pushing it to origin `plotly/dash`, doing so leaves no chance of making an embarrasing public exposé.

```bash
# install the cli (first time only)
$ curl -fLSs https://circle.ci/cli | bash && circleci version

# trigger a local circleci container session
# you should run at least one python version locally
# note: the current config requires all tests pass on python 2.7, 3.6 and 3.7.
$ circleci local execute --job python-3.6
```
### Coding Style

We use both `flake8` and `pylint` for basic linting check, please refer to the relevant steps in `.circleci/config.yml`.

## Tests

We started migrating to [pytest](https://docs.pytest.org/en/latest/) from `unittest` as our test automation framework. You will see more testing enhancements in the near future.

### Unit Tests

For simple API changes, please add adequate unit tests under `/tests/unit`

Note: *You might find out that we have more integration tests than unit tests in Dash. This doesn't mean unit tests are not important, the [test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) is still valid. Dash project has its unique traits which needs more integration coverage than typical software project, another reason was that dash was a quick prototype crafted by chris in a lovely montreal summer.*

### Integration Tests

We create various miminal dash apps to cover feature scenario. A server is launched in mutli-thread or multi-process flavor and the test steps are executed in browsers driving by selenium webdrivers.

Any reasonable test scenario is encouraged to be added along with the same PR.

### Visual regression with Percy

Testing graph-intensive-application is a challenging job. We use [percy](https://percy.io/) to mitigate the pain, please pay attention if percy reports visual differences. If you are not sure whether the change is expected, leave a comment, and don't blind-approve it.


## Test variable tips
You can configure the test server with the following variables:

### DASH_TEST_CHROMEPATH
If you run a special chrome, set the path to your chrome binary with this environment variable.

### DASH_TEST_PROCESSES
If you encounter errors about Multi-server + Multi-processing when running under Python 3, try running the tests with the number of server processes set to 1.

### Example: single test run with configuration

```bash
DASH_TEST_CHROMEPATH=/bin/google-chrome-beta DASH_TEST_PROCESSES=1
pytest -k test_no_callback_context
```

## Financial Contributions

Dash, and many of Plotly's open source products, have been funded through direct sponsorship by companies. [Get in touch] about funding feature additions, consulting, or custom app development.

[Dash Core Components]: https://dash.plot.ly/dash-core-components
[Dash HTML Components]: https://github.com/plotly/dash-html-components
[write your own components]: https://dash.plot.ly/plugins
[Dash Component Biolerplate]: https://github.com/plotly/dash-component-boilerplate
[issues]: https://github.com/plotly/dash-core-components/issues
[GitHub flow]: https://guides.github.com/introduction/flow/
[semantic versioning]: https://semver.org/
[Dash Community Forum]: https://community.plot.ly/c/dash
[Get in touch]: https://plot.ly/products/consulting-and-oem
[Documentation]: https://github.com/orgs/plotly/projects/8
[Dash Docs]: https://github.com/plotly/dash-docs
