const options = {
    ts: {
        transpileOnly: true
    },
    preprocessor: {
        definitions: ['TEST', 'TEST_COPY_PASTE']
    },
    mode: 'development'
};

const config = require('./.config/webpack/base.js')(options);

module.exports = config;