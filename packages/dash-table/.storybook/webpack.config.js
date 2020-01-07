let babel = require('./babel.config.js');
let config = require('./../.config/webpack/base.js')({
    babel,
    ts: {
        transpileOnly: true
    },
    preprocessor: {
        variables: {
            mode: 'eager'
        }
    }
});

config.externals = {};
delete config.plugins;

module.exports = config;