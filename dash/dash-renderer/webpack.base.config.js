const webpack = require('webpack');
const R = require('ramda');
const path = require('path');
const packagejson = require('./package.json');
const dashLibraryName = packagejson.name.replace(/-/g, '_');

// Externalized react/jsx-runtime. Newer Dash provides window.ReactJSXRuntime
// (see src/react-shim.js) backed by the React version loaded on the page;
// the inline fallback keeps bundles built this way working on older Dash,
// which does not define the global. Keep in sync with react-shim.js.
const jsxRuntimeExternal = `var (window.ReactJSXRuntime || (window.ReactJSXRuntime = (function (React) {
    function jsx(type, config, maybeKey) {
        var props = {};
        var children = null;
        if (config != null) {
            if (config.key !== undefined) {
                props.key = '' + config.key;
            }
            for (var propName in config) {
                if (
                    Object.prototype.hasOwnProperty.call(config, propName) &&
                    propName !== 'key' &&
                    propName !== '__self' &&
                    propName !== '__source'
                ) {
                    if (propName === 'children') {
                        children = config[propName];
                    } else {
                        props[propName] = config[propName];
                    }
                }
            }
        }
        if (maybeKey !== undefined) {
            props.key = '' + maybeKey;
        }
        if (children === null || children === undefined) {
            return React.createElement(type, props);
        }
        return Array.isArray(children)
            ? React.createElement.apply(React, [type, props].concat(children))
            : React.createElement(type, props, children);
    }
    return {jsx: jsx, jsxs: jsx, jsxDEV: jsx, Fragment: React.Fragment};
})(window.React)))`;

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

// WebSocket Worker configuration
const workerOptions = {
    mode: 'production',
    entry: {
        'dash-ws-worker': '../../@plotly/dash-websocket-worker/src/worker.ts',
    },
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
                use: ['ts-loader'],
            },
        ]
    },
    resolve: {
        extensions: ['.ts', '.js']
    }
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
    ]),
    // WebSocket Worker build
    workerOptions,
    // React compatibility shim build
    shimOptions
];
