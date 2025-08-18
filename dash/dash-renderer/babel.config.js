module.exports = {
    presets: [
        '@babel/preset-typescript',
        ['@babel/preset-env', {
            "targets": {
                "browsers": ["last 10 years and not dead"]
            }
        }],
        '@babel/preset-react'
    ],
    plugins: [
        '@babel/plugin-proposal-class-properties',
        '@babel/plugin-transform-optional-chaining',
    ],
};
