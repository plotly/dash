const webpack = require('webpack');
const R = require('ramda');
const path = require('path');
const packagejson = require('./package.json');
const dashLibraryName = packagejson.name.replace(/-/g, '_');

const defaults = {
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
                test: /\.jsx?$/,
                include: /node_modules[\\\/](cytoscape-fcose|ramda|react-cytoscapejs|react-redux)[\\\/]/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        babelrc: false,
                        configFile: false,
                        presets: [
                            '@babel/preset-env'
                        ]
                    }
                }
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
        path: path.resolve(__dirname, "build"),
        filename: `${dashLibraryName}.dev.js`,
        library: {
            name: dashLibraryName,
            type: 'window',
        }
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
        rendererOptions,
        {
            // with default eval sourcemap we can't es-check the dev bundle
            devtool: 'inline-source-map'
        }
    ]),
    R.mergeAll([
        options,
        rendererOptions,
        {
            mode: 'production',
            output: {
                path: path.resolve(__dirname, "build"),
                filename: `${dashLibraryName}.min.js`,
                library: {
                    name: dashLibraryName,
                    type: 'window',
                }
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
