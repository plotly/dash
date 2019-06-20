const options = {
    ts: {
        transpileOnly: true
    },
    preprocessor: {
        definitions: ['TEST', 'TEST_COPY_PASTE']
    },
    mode: 'development'
};

module.exports = require('./.config/webpack/base.js')(options);