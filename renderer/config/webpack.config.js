var path = require('path');

var ROOT = process.cwd();
var SRC = path.join(ROOT, 'src');
var BUILD = path.join(ROOT, 'build');

module.exports = {
    cache: false,
    // Resolution path for `entry`.
    context: SRC,
    entry: {
        bundle: './index.js'
    },
    output: {
        path: BUILD,
        filename: '[name].js'
    },
    resolve: {
        // Need `''` so referencing modules by `name.js` works.
        extensions: ['', '.js', '.jsx']
    },
    module: {
        loaders: [
            {
                test: /\.js/,
                include: [SRC],
                /*
                 * Use require.resolve to get a deterministic path
                 * and avoid webpack's magick loader resolution
                 */
                loader: require.resolve('babel-loader'),
                query: {
                    presets: ['es2015', 'react']
                }
            }
        ]
    }
};
