const webpack = require('webpack');
const R = require('ramda');
const path = require('path');
const packagejson = require('./package.json');
const dashLibraryName = packagejson.name.replace(/-/g, '_');

const defaults = {
    plugins: [
        new webpack.ProvidePlugin({
            Buffer: ['buffer', 'Buffer'],
            process: 'process/browser',
        }),
    ],
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
        extensions: ['.js', '.ts', '.tsx'],
        alias: {
            zlib: require.resolve('browserify-zlib'),
            stream: require.resolve('stream-browserify'),
            fs: require.resolve('browserify-fs'),
            path: require.resolve('path-browserify'),
            buffer: require.resolve('buffer'),
        },
    }
};

const rendererOptions = {
    mode: 'development',
    entry: {
        main: ['whatwg-fetch', './src/index.js'],
    },
    output: {
        path: path.resolve(__dirname, "build"),
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

module.exports = options => [
    R.mergeAll([
        options,
        rendererOptions
    ]),
    R.mergeAll([
        options,
        rendererOptions,
        {
            mode: 'production',
            output: {
                path: path.resolve(__dirname, "build"),
                filename: `${dashLibraryName}.min.js`,
                library: dashLibraryName,
                libraryTarget: 'window',
            },
            plugins: R.concat(
                options.plugins || [],
                [
                    new webpack.NormalModuleReplacementPlugin(
                        /(.*)GlobalErrorContainer.react(\.*)/,
                        function (resource) {
                            resource.request = resource.request.replace(
                                /GlobalErrorContainer.react/,
                                'GlobalErrorContainerPassthrough.react'
                            );
                        }
                    ),
                ]
            ),
        }
    ])
];
