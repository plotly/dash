'use strict';

var partial = require('webpack-partial').default;

module.exports = function (config) {
    return partial(config, {
        entry: {
            bundle: [
                'webpack-dev-server/client?http://localhost:8080',
                './index.js',
                'webpack/hot/only-dev-server'

            ]
        }
    });
};
