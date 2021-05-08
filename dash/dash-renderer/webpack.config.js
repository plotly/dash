const webpack = require('webpack');
const R = require('ramda');
const path = require('path');
const packagejson = require('./package.json');
const dashLibraryName = packagejson.name.replace(/-/g, '_');

const defaults = {
    plugins: [],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                },
            },
            {
                test: /\.ts(x?)$/,
                exclude: /node_modules/,
                use: ['babel-loader', 'ts-loader'],
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /\.svg$/,
                use: ['@svgr/webpack'],
            }
        ]
    },
    resolve: {
        extensions: ['.js', '.ts', '.tsx']
    }
};

const rendererOptions = {
    mode: 'development',
    entry: {
        main: ['whatwg-fetch', './src/index.js'],
    },
    output: {
        path: path.resolve(__dirname, "..", "deps"),
        filename: `${dashLibraryName}.dev.js`,
        library: dashLibraryName,
        libraryTarget: 'window',
    },
    externals: {
        react: 'React',
        'react-dom': 'ReactDOM',
        'prop-types': 'PropTypes'
    },
    ...defaults
};

module.exports = (_, argv) => {
    const devtool = argv.build === 'local' ? 'source-map' : 'none';
    return [
        R.mergeDeepLeft({ devtool }, rendererOptions),
        R.mergeDeepLeft({
            devtool,
            mode: 'production',
            output: {
                filename: `${dashLibraryName}.min.js`,
            },
            plugins: [
                new webpack.NormalModuleReplacementPlugin(
                    /(.*)GlobalErrorContainer.react(\.*)/,
                    function (resource) {
                        resource.request = resource.request.replace(
                            /GlobalErrorContainer.react/,
                            'GlobalErrorContainerPassthrough.react'
                        );
                    }
                ),
            ],
        }, rendererOptions)
    ];
};
