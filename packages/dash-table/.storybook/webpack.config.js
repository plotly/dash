let babel = require('./babel.config.js');
let config = require('./../.config/webpack/base.js')({
    babel
});

config.externals = {};

module.exports = config;