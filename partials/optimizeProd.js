'use strict';

var partial = require('webpack-partial').default;
var UglifyJsPlugin = require('webpack').optimize.UglifyJsPlugin;
var DedupePlugin = require('webpack').optimize.DedupePlugin;
var OccurrenceOrderPlugin = require('webpack').optimize.OccurrenceOrderPlugin;

module.exports = function (config) {
    return partial(config, {
        plugins: [
            new DedupePlugin(),
            new OccurrenceOrderPlugin(true),
            new UglifyJsPlugin({
                compress: {
                    warnings: false
                }
            })
        ]
    });
};
