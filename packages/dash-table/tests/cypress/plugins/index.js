const wp = require('@cypress/webpack-preprocessor');

module.exports = on => {
    const options = {
        webpackOptions: require('../../../webpack.test.standalone.config.js')
    };

    on('file:preprocessor', wp(options));

    on('before:browser:launch', (browser = {}, args) => {
        if (browser.name === 'chrome') {
            // ^ make sure this is your browser name, you may
            // be using 'canary' or 'chromium' for example, so change it to match!
            args.push('--proxy-bypass-list=<-loopback>');
            return args;
        }
    });
};