'use strict';

var partial = require('webpack-partial').default;
var CleanWebpackPlugin = require('clean-webpack-plugin');

var ROOT = process.cwd();

module.exports = function(config) {
    return partial(config, {
        plugins: [
            new CleanWebpackPlugin(['build'], {
                root: ROOT,
                verbose: true,
                dry: false
            })
        ]
    });
};
