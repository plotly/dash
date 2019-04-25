const config = require('./.config/webpack/base.js')(
    {
        definitions: ['TEST_COPY_PASTE']
    },
    'development'
);

config.module.rules.forEach(rule => {
    if (rule.loader) {
        rule.loader = rule.loader.replace('ts-loader', `ts-loader?${JSON.stringify({ transpileOnly: true })}`);
    }
});

module.exports = config;