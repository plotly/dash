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
        extensions: ['', '.js', '.jsx']
    }
};
