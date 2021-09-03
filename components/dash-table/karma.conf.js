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
            'tests/js-unit/**/*.ts': ['webpack']
        },
        files: [
            'node_modules/babel-polyfill/dist/polyfill.js',
            'node_modules/regenerator-runtime/runtime.js',
            'tests/js-unit/**/*.ts' // *.tsx for React Jsx
        ],
        reporters: ["progress"],
        browsers: ["Chrome"],
        webpack: require('./webpack.test.config')
    });
}