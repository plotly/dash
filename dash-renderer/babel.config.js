module.exports = {
    presets: [['@babel/preset-env', {
        useBuiltIns: 'usage',
        corejs: 3
    }], '@babel/preset-react'],
    env: {
        test: {
            plugins: [
                '@babel/plugin-transform-modules-commonjs'
            ]
        }
    }
};
