module.exports = {
    presets: [
        '@babel/preset-typescript',
        '@babel/preset-env',
        '@babel/preset-react'
    ],
    plugins: [
        '@babel/plugin-proposal-class-properties',
    ],
    env: {
        test: {
            plugins: [
                '@babel/plugin-proposal-class-properties',
                '@babel/plugin-transform-modules-commonjs'
            ]
        }
    }
};
