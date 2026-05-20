const path = require('path');

// This config is for standalone development/testing of the worker.
// The production build is handled by dash-renderer's webpack config.
module.exports = {
    entry: './src/worker.ts',
    output: {
        filename: 'dash-ws-worker.js',
        path: path.resolve(__dirname, 'dist'),
        clean: true
    },
    resolve: {
        extensions: ['.ts', '.js']
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: 'ts-loader',
                exclude: /node_modules/
            }
        ]
    },
    target: 'webworker'
};
