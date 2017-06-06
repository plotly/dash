'use strict';

var partial = require('webpack-partial').default;

module.exports = function (config) {
    return partial(config, {
        entry: {
            bundle: [
                require.resolve('webpack-dev-server/client') + '?http://localhost:8080',
                require.resolve('webpack/hot/only-dev-server'),
                '../demo/index.js'
            ]
        }
    });
};
