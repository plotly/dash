'use strict';

var path = require('path');
var partial = require('webpack-partial').default;

var ROOT = process.cwd();
var BUILD = path.join(ROOT, 'build');

module.exports = function (config) {
    return partial(config, {
        output: {
            path: BUILD,
            publicPath: '/build/',
            // TODO: Bundle filename should be hashed (#10)
            filename: '[name].js'
        }
    });
};
