'use strict';

var path = require('path');
var partial = require('webpack-partial').default;

var ROOT = process.cwd();
var SRC = path.join(ROOT, 'src');
var DEMO = path.join(ROOT, 'demo');

module.exports = function (config) {
    return partial(config, {
        module: {
            noParse: /node_modules\/json-schema\/lib\/validate\.js/, // used to get `request` to work: https://github.com/request/request/issues/1920#issuecomment-171246043
            loaders: [
                { test: /\.json$/, loader: 'json-loader' },
                {
                    test: /\.js/,
                    include: [SRC, DEMO],
                    /*
                     * Use require.resolve to get a deterministic path
                     * and avoid webpack's magick loader resolution
                     */
                    loaders: [
                        require.resolve('react-hot-loader'),
                        require.resolve('babel-loader')
                    ]
                }
            ]
        }
    });
};
