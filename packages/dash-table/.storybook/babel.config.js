const presets = [
    ['@babel/env', {
        useBuiltIns: 'entry',
        corejs: 3
    }],
    '@babel/preset-react'
];

const plugins = [
    '@babel/plugin-transform-regenerator'
];

module.exports = { presets, plugins };
