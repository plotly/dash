module.exports = config => {
    config.set({
        frameworks: ['mocha', 'webpack'],

        plugins: [
            'karma-webpack',
            'karma-mocha',
            'karma-chrome-launcher'
        ],
        preprocessors: {
            // add webpack as preprocessor
            'tests/**/*.{js,ts}': ['webpack']
        },
        files: [
            'node_modules/regenerator-runtime/runtime.js',
            'tests/**/*.{js,ts}'
        ],
        reporters: ["progress"],
        browsers: ["Chrome"],
        webpack: require('./webpack.test.config.js')[0],
        client: {
            mocha: {
                timeout: 5000
            }
        }
    });
}
