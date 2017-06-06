'use strict';
/**
 * Webpack frontend test (w/ coverage) configuration.
 */
var archDevRequire = require('dash-components-archetype-dev/require');
var _ = archDevRequire('lodash'); // devDependency
var testCfg = require('./webpack.config.test');

module.exports = _.merge({}, testCfg, {
    module: {
        preLoaders: [
            // Manually instrument client code for code coverage.
            // https://github.com/deepsweet/isparta-loader handles ES6 + normal JS.
            {
                test: /src\/.*\.js$/,
                exclude: /(test|node_modules)\//,
                loader: archDevRequire.resolve('isparta-loader')
            }
        ]
    }
});
