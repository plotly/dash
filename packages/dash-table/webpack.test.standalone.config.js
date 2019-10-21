const options = {
    ts: {
        transpileOnly: true
    },
    preprocessor: {
        variables: {
            mode: 'eager'
        },
        definitions: ['TEST', 'TEST_COPY_PASTE']
    },
    mode: 'development'
};

let config = require('./.config/webpack/base.js')(options);
delete config.plugins;

module.exports = config;