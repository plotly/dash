const options = {
    entry: ['@babel/polyfill'],
    ts: {
        transpileOnly: true
    },
    preprocessor: {
        definitions: ['TEST', 'TEST_COPY_PASTE'],
        variable: {
            mode: 'eager'
        }
    },
    mode: 'development'
};

let config = require('./.config/webpack/base.js')(options);

module.exports = config;