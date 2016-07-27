# Dash Components Core

This package provides the core React component suite for [Dash2][].

## Development

### Demo server

You can start up a demo development server to see a demo of the rendered
components:

```sh
$ builder run demo
$ open http://localhost:9000
```

You have to maintain the list of components in `demo/Demo.react.js`.

### Code quality and tests

#### To run lint and unit tests:

```sh
$ npm test
```

#### To run unit tests and watch for changes:

```sh
$ npm run test-watch
```

#### To debug unit tests in a browser (Chrome):

```sh
$ npm run test-debug
```

1. Wait until Chrome launches.
2. Click the "DEBUG" button in the top right corner.
3. Open up Chrome Devtools (`Cmd+opt+i`).
4. Click the "Sources" tab.
5. Find source files
  - Navigate to `webpack:// -> . -> spec/components` to find your test source files.
  - Navigate to `webpack:// -> [your/repo/path]] -> dash-core-components -> src` to find your component source files.
6. Now you can set breakpoints and reload the page to hit them.
7. The test output is available in the "Console" tab, or in any tab by pressing "Esc".

#### To run a specific test

In your test, append `.only` to a `describe` or `it` statement:

```javascript
describe.only('Foo component', () => {
    // ...
})l
```

### Testing your components in Dash

The best way to test your components in the real Dash context is by linking into
`dash2` and testing them from there.

1. Prepare module by linking and watching for changes

        # Symlink module
        $ npm link

        # Transpile components to `lib/` and watch for changes
        $ npm start

2. Link module into `dash2` project

        # In the `dash2/renderer` project directory:
        $ npm link dash-core-components

Now you should be able to restart the webpack process (in `dash2/renderer`:
`ctrl-c`, `npm start`), after which webpack will automatically pick up new
changes to the component suite.

## Installing python package locally

You don't need publishing access to test the module locally.

```sh
# Install in `site-packages` on your machine
$ python setup.py install
```

## Publishing

For now, two different workflows are necessary for publishing to NPM and PyPi,
respectively. TODO:
[#5](https://github.com/plotly/dash-components-archetype/issues/5) will roll up
publishing steps into one workflow.

Ask @chriddyp to be added to the [NPM package authors][] or to [PyPi][].

### Publishing to NPM

```sh
# Bump the package version
$ npm version major|minor|patch

# Push branch and tags to repo
$ git push --follow-tags

# Publish to NPM (will run tests as a pre-publish step)
$ npm publish
```

### Publishing to PyPi

```sh
# Bump the package version
$ vi setup.py

# Commit to github
$ git add setup.py
$ git commit -m "Bump pypi package version to vx.x.x"

# Publish to PyPi
$ npm run publish-pypi
```

## Builder / Archetype

We use [Builder][] to centrally manage build configuration, dependencies, and
scripts.

To see all `builder` scripts available:

```sh
$ builder help
```

See the [dash-components-archetype][] repo for more information.

[Builder]: https://github.com/FormidableLabs/builder
[Dash2]: https://github.com/plotly/dash2
[NPM package authors]: https://www.npmjs.com/package/dash-core-components/access
[PyPi]: https://pypi.python.org/pypi
