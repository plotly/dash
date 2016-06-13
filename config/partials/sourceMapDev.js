'use strict';

var partial = require('webpack-partial').default;
var SourceMapDevToolPlugin = require('webpack').SourceMapDevToolPlugin;

module.exports = function (config) {
    return partial(config, {
        plugins: [
            new SourceMapDevToolPlugin({
                append: '\n//# sourceMappingURL=http://127.0.0.1:8080/build/[url]',
                filename: '[file].map',
                test: /\.(css|js)($|\?)/
            })
        ]
    });
};
