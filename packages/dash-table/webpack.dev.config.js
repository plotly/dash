const options = {
    preprocessor: {
        definitions: ['DEV']
    },
    mode: 'development'
};

module.exports = require('./.config/webpack/base.js')(options);