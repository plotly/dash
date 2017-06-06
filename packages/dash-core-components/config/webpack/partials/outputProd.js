'use strict';

var path = require('path');
var partial = require('webpack-partial').default;
var inferNamespace = require('../infer-namespace');

var ROOT = process.cwd();
var BUILD_PATH = path.join(ROOT, 'lib');
var LIBRARY_NAME = inferNamespace(ROOT);

module.exports = function (config) {
    return partial(config, {
        output: {
            library: LIBRARY_NAME,
            libraryTarget: 'this', // Could be 'umd'
            path: BUILD_PATH,
            filename: '[name].js'
        }
    });
};
