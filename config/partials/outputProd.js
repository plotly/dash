'use strict';

var path = require('path');
var partial = require('webpack-partial').default;

var ROOT = process.cwd();
var BUILD = path.join(ROOT, 'dash_renderer');

module.exports = function (config) {
    return partial(config, {
        output: {
            path: BUILD,
            publicPath: '/dash_renderer/',
            library: 'dash_renderer',
            // TODO: Bundle filename should be hashed (#10)
            filename: '[name].js'
        }
    });
};
