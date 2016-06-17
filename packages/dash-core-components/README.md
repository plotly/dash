# Dash Components Core

This package provides the core React component suite for [Dash2][].

## Development

We don't yet have a dev server with demo capabilities in this repo. The best way
to test your components is by linking into `dash2` and testing them from there.

1. Prepare module by linking and watching for changes

        # Symlink module
        $ npm link

        # Transpile components to `lib/` and watch for changes
        $ npm start

2. Link module into `dash2` project

        # In the `dash2/renderer` project directory:
        $ npm link dash-components-core

Now you should be able to restart the webpack process (in `dash2/renderer`:
`ctrl-c`, `npm start`), after which webpack will automatically pick up new
changes to the component suite.

## Publishing

Ask @coopy or @chriddyp to be added to the [NPM package authors][].

```sh
# Bump the package version
$ npm version major|minor|patch

# Push branch and tags to repo
$ git push --follow-tags

# Publish to NPM (will run tests as a pre-publish step)
$ npm publish
```

[Dash2]: https://github.com/plotly/dash2
[NPM package authors]: https://www.npmjs.com/package/dash-components-core/access
