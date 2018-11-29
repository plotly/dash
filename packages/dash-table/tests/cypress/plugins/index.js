const wp = require('@cypress/webpack-preprocessor');

module.exports = on => {
    const options = {
        webpackOptions: require('../../../webpack.test.config.js')
    };

    on('file:preprocessor', wp(options));
};