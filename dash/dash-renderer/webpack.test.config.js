const NodePolyfillPlugin = require('node-polyfill-webpack-plugin');
const config = require('./webpack.base.config');

module.exports = config({
    plugins: [
        new NodePolyfillPlugin()
    ]
});