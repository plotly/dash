# dash-html-components

Vanilla HTML components for Dash

## Dash

Go to this link to learn about [Dash][].

## Getting started

```sh
# Install dependencies
$ npm install

# Watch source for changes and build to `lib/`
$ npm start
```

## Development

We don't yet have a dev server with demo capabilities. The best way to test
your components is by linking into `dash2` and testing them from there.

1. Prepare module by linking and watching for changes

        # Symlink module
        $ npm link

        # Transpile components to `lib/` and watch for changes
        $ npm start

2. Link module into `dash2` project

        # In the `dash2/renderer` project directory:
        $ npm link [YOUR-COMPONENT-SUITE-NAME]

Now you should be able to restart the webpack process (in `dash2/renderer`:
`ctrl-c`, `npm start`), after which webpack will automatically pick up new
changes to the component suite.

## Builder / Archetype

We use [Builder][] to centrally manage build configuration, dependencies, and
scripts. See the [dash-components-archetype][] repo for more information.


[Builder]: https://github.com/FormidableLabs/builder
[Dash]: https://github.com/plotly/dash2
[dash-components-archetype]: https://github.com/plotly/dash-components-archetype
