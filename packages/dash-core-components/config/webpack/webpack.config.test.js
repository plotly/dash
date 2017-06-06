'use strict';
/**
 * Webpack frontend test configuration.
 * TODO: Refactor to take advantage of composable webpack configuration partials
 * https://github.com/plotly/dash-components-archetype/issues/13
 */
var path = require('path');

// Replace with `__dirname` if using in project root.
var ROOT = process.cwd();

// Stash the location of `<archetype-dev>/node_modules`
//
// A normal `require.resolve` looks at `package.json:main`. We instead want
// just the _directory_ of the module. So use heuristic of finding dir of
// package.json which **must** exist at a predictable location.
var archetypeDevNodeModules = path.join(
    path.dirname(require.resolve('dash-components-archetype-dev/package.json')),
    'node_modules'
);

/* AND NOW EXPORT THE CONFIGURATION */
module.exports = {
    cache: true,
    context: path.join(ROOT, 'test'),
    devtool: 'inline-source-map',
    entry: './main',
    externals: {
        'cheerio': 'window',
        'react/addons': true,
        'react/lib/ExecutionEnvironment': true,
        'react/lib/ReactContext': true
    },
    output: {
        filename: 'main.js',
        publicPath: '/assets'
    },
    resolve: {
        extensions: ['', '.js', '.json'],
        root: [archetypeDevNodeModules]
    },
    resolveLoader: {
        root: [archetypeDevNodeModules]
    },

    module: {
        loaders: [
            {
                test: /\.js?$/,
                exclude: [/node_modules/],
                // **Note**: Cannot use shorthand `'babel-loader'` or `'babel'` when
                // we are playing around with `NODE_PATH` in builder. Manually
                // resolve path.
                loader: require.resolve('babel-loader')
            }, {
                test: /\.json$/,
                loader: require.resolve('json-loader')
            }
        ]
    }
};
