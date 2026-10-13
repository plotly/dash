const webpack = require('webpack');
const R = require('ramda');
const path = require('path');
const packagejson = require('./package.json');
const {jsxRuntimeExternal} = require('./jsx-runtime-external');
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
                include: /node_modules[\\\/](cytoscape-fcose|ramda|react-cytoscapejs|react-redux|cookie)[\\\/]/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        babelrc: false,
                        configFile: false,
                        presets: [
                            '@babel/preset-env'
                        ],
                        plugins: [
                            '@babel/plugin-transform-optional-chaining'
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
        'react/jsx-runtime': jsxRuntimeExternal,
        'react/jsx-dev-runtime': jsxRuntimeExternal,
        'prop-types': 'PropTypes'
    },
    ...defaults
};

// Standalone React compatibility shim, loaded right after react/react-dom
// and before any component package (see _js_dist_dependencies).
const shimOptions = {
    mode: 'production',
    entry: {
        'react-shim': './src/react-shim.js',
    },
    output: {
        path: path.resolve(__dirname, "build"),
        filename: '[name].min.js',
    }
};

// SharedWorker bundles. Each worker gets its own compilation with an explicit
// tsconfig: ts-loader would otherwise type-check both entries against
// whichever tsconfig it finds first, and the two need different libs
// (WebWorker for the WebSocket worker package, the renderer's DOM lib for the
// stream worker, which shares its transport code with the page).
const workerConfig = (name, entry, configFile) => ({
    mode: 'production',
    entry: {[name]: entry},
    output: {
        path: path.resolve(__dirname, "build"),
        filename: '[name].js',
    },
    target: 'webworker',
    module: {
        rules: [
            {
                test: /\.ts$/,
                exclude: /node_modules/,
                use: [{loader: 'ts-loader', options: {configFile}}],
            },
        ]
    },
    resolve: {
        extensions: ['.ts', '.js']
    }
});

// WebSocket Worker configuration
const workerOptions = workerConfig(
    'dash-ws-worker',
    '../../@plotly/dash-websocket-worker/src/worker.ts',
    path.resolve(__dirname, '../../@plotly/dash-websocket-worker/tsconfig.json')
);

// Streaming downlink worker configuration
const streamWorkerOptions = workerConfig(
    'dash-stream-worker',
    './src/workers/streamWorker.ts',
    path.resolve(__dirname, 'tsconfig.json')
);

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
    ]),
    // SharedWorker builds (WebSocket transport, streaming downlink)
    workerOptions,
    streamWorkerOptions,
    // React compatibility shim build
    shimOptions
];
