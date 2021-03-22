const path = require('path');

const baseConfig = require('./../.config/webpack/base.js')({
    ts: {
        transpileOnly: true
    },
    preprocessor: {
        variables: {
            mode: 'eager'
        }
    }
});

module.exports = {
    core: { builder: 'webpack5' },
    stories: ['./../tests/visual/percy-storybook/**/*.percy.tsx'],
    webpackFinal: async (config, { configType }) => {
        // jerry rig everything
        config.resolve.alias.core = path.resolve(__dirname, './../src/core'),
        config.resolve.alias['dash-table'] = path.resolve(__dirname, './../src/dash-table')

        config.module = baseConfig.module;
        config.stats = {
            warnings: true
        };

        return config;
    }
};