const webpack = require('webpack');
const R = require('ramda');
const path = require('path');
const packagejson = require('./package.json');
const dashLibraryName = packagejson.name.replace(/-/g, '_');
const { WebpackPluginServe: Serve } = require('webpack-plugin-serve');


const defaults = {
    plugins: [
        new Serve(
            {
                port: 5000,
                /* we need to proxy the call to the relevant dash app, in addition, we need to rewrite
                 * for the second path, as dash app are by default mountained on the root path '/'
                 */
                middleware: (app, builtins) => {
                    app.use(builtins.proxy('/_dash-*', {target: 'http://localhost:9000'}));
                    app.use(builtins.proxy('/second/_dash-*', {
                        pathRewrite: {
                            '/second': ''
                        },
                        target: 'http://localhost:8050'
                    }));
                }
            })
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
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /\.svg$/,
                use: ['@svgr/webpack'],
            }
        ]
    }
};

const rendererOptions = {
    mode: 'development',
    entry: {
        main: ['whatwg-fetch', './src/index.js'],
    },
    output: {
        path: path.resolve(__dirname, dashLibraryName),
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
