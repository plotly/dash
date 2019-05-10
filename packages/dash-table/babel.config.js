const presets = [
    ['@babel/env', {
        targets: {
            browsers: [
                'last 2 Chrome versions',
                'last 2 Firefox versions',
                'last 2 Safari versions',
                'last 2 Edge versions',
                'Explorer 11'
            ]
        },
        useBuiltIns: 'usage',
        corejs: 3
    }],
    '@babel/preset-react'
];

const plugins = [
    '@babel/plugin-syntax-dynamic-import'
];

module.exports = { presets };
