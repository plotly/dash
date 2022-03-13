# Contributing to dash-core-components

## Getting Started

Refer to the [readme](README.md) for installation and development instructions.

## Contributions

[Dash Core Components][] consist of pluggable components for creating interactive user interfaces. For generic HTML5 elements, see [Dash HTML Components][]. Contributions are welcome! This repository's open [issues][] are a good place to start. Another way to contribute is to [write your own components][] using for instance the [component boilerplate](https://github.com/plotly/dash-component-boilerplate).

## Coding Style

Please lint any additions to react components with `npm run lint`. Rules defined in [.eslintrc](.eslintrc) are inherited from [`dash-components-archetype`](https://github.com/plotly/dash-components-archetype)'s [eslintrc-react.json][]

## Pull Request Guidelines

Use the [GitHub flow][] when proposing contributions to this repository (i.e. create a feature branch and submit a PR against the master branch).

## Making a Contribution
_For larger features, your contribution will have a higher likelihood of getting merged if you create an issue to discuss the changes that you'd like to make before you create a pull request._

1. Create a pull request.
2. After a review has been done and your changes have been approved, they will be merged and included in a future release of Dash.
3. If significant enough, you have created an issue about documenting the new feature or change and you have added it to the [dash-docs](https://github.com/plotly/dash-docs) project.

## Running the Tests

In order to run the tests, you first need to have built the JavaScript
`dash_core_components` library. You will need to build the library again if
you've pulled from upstream otherwise you may be running with an out of date
`bundle.js`. See the instructions for building `bundle.js` in the [Testing
Locally](README.md#testing-locally) section of README.md.

## Updating official version of Plotly.js

1. Update the version of `plotly.js-dist-min` in package.json. Always use an exact version without "^" or "~"
2. Run `npm install` followed by `npm run build`, the Plotly.js artifact will be copied and bundled over as required
4. Update `CHANGELOG.md` with links to the releases and a description of the changes. The message should state (see the existing `CHANGELOG.md` for examples):
    * If you're only bumping the patch level, the heading is "Fixed" and the text starts "Patched plotly.js". Otherwise the heading is "Updated" and the text starts "Upgraded plotly.js"
    * The new plotly.js version number, and the PR in which this was done
    * All major or minor versions included, with links to their release pages and a summary of the major new features in each. If there are multiple minor/major releases included, be sure to look at all of their release notes to construct the summary. Call minor versions "feature" versions for the benefit of users not steeped in semver terminology.
    * All patch versions included, with links to their release pages and a note that these fix bugs
5. When bumping the dcc version, a plotly.js patch/minor/major constitutes a dcc patch/minor/major respectively as well.

### Using a temporary `plotly.js-dist-min` package (or other dependencies)

> During integrated development of new features or bug fixes in plotly.js and dash, it may be required to install a temporary plotly.js-dist-min package (or other packages) including proposed changes. To do so, please place the `.tgz` file in `packages/` folder then `npm install` the file.


## Financial Contributions

If your company wishes to sponsor development of open source dash components, please [get in touch][].

[Dash Core Components]: https://dash.plotly.com/dash-core-components
[Dash HTML Components]: https://github.com/plotly/dash-html-components
[write your own components]: https://dash.plotly.com/plugins
[Dash Components Archetype]: https://github.com/plotly/dash-components-archetype
[issues]: https://github.com/plotly/dash-core-components/issues
[GitHub flow]: https://guides.github.com/introduction/flow/
[eslintrc-react.json]: https://github.com/plotly/dash-components-archetype/blob/master/config/eslint/eslintrc-react.json
[contributors]: https://github.com/plotly/dash-core-components/graphs/contributors
[semantic versioning]: https://semver.org/
[Dash Community Forum]: https://community.plotly.com/c/dash
[Confirmation Modal component]: https://github.com/plotly/dash-core-components/pull/211#issue-195280462
[Confirmation Modal announcement]: https://community.plotly.com/t/announcing-dash-confirmation-modal-feedback-welcome/11627
[get in touch]: https://plotly.com/products/consulting-and-oem
