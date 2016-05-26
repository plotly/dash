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
            filename: '[name].js'
        }
    });
};