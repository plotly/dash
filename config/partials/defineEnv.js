'use strict';

var partial = require('webpack-partial').default;
var DefinePlugin = require('webpack').DefinePlugin;

var NODE_ENV = process.env.NODE_ENV || 'development';
var environment = JSON.stringify(NODE_ENV);

/* eslint-disable no-console */
console.log('Current environment: ' + environment);
/* eslint-enable no-console */

module.exports = function (config) {
    return partial(config, {
        plugins: [
            new DefinePlugin({
                'process.env': {
                    NODE_ENV: environment
                }
            })
        ]
    });
};
