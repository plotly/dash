'use strict';

var path = require('path');

var ROOT = process.cwd();
var SRC = path.join(ROOT, 'src');

module.exports = {
    cache: false,
    // Resolution path for `entry`.
    context: SRC,
    resolve: {
        // Need `''` so referencing modules by `name.js` works.
        extensions: ['', '.js', '.jsx', '.json'],
        // Make default module directory explicit
        modulesDirectories: ['node_modules']
    },
    // Support `request` node library
    node: {
        console: true,
        fs: 'empty',
        net: 'empty',
        tls: 'empty'
    }
};
