const path = require('path');
const webpack = require('webpack');
const NodePolyfillPlugin = require("node-polyfill-webpack-plugin");
const WebpackDashDynamicImport = require('@plotly/webpack-dash-dynamic-import');

const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

// Externalized react/jsx-runtime. Newer Dash provides window.ReactJSXRuntime
// (see dash-renderer/src/react-shim.js) backed by the React version loaded on
// the page; the inline fallback keeps this bundle working on older Dash,
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

module.exports = (env, argv) => {

    let mode;

    const overrides = module.exports || {};

    // if user specified mode flag take that value
    if (argv && argv.mode) {
        mode = argv.mode;
    }

    // else if configuration object is already set (module.exports) use that value
    else if (overrides.mode) {
        mode = overrides.mode;
    }

    // else take webpack default (production)
    else {
        mode = 'production';
    }

    let filename = (overrides.output || {}).filename;
    if (!filename) {
        filename = `${dashLibraryName}.js`;
    }

    const entry = overrides.entry || { main: './src/index.ts' };

    const externals = ('externals' in overrides) ? overrides.externals : ({
        react: 'React',
        'react-dom': 'ReactDOM',
        'react/jsx-runtime': jsxRuntimeExternal,
        'react/jsx-dev-runtime': jsxRuntimeExternal,
        'prop-types': 'PropTypes'
    });

    return {
        mode,
        entry,
        target: ['web', 'es5'],
        output: {
            path: path.resolve(__dirname, dashLibraryName),
            chunkFilename: '[name].js',
            filename,
            library: {
                name: dashLibraryName,
                type: 'window',
            }
        },
        externals,
        resolve: {
            extensions: ['.ts', '.tsx', '.js', '.jsx', '.json']
        },
        module: {
            noParse: /node_modules[\\\/]plotly.js-dist-min/,
            rules: [
                // TypeScript loader
                {
                    test: /\.tsx?$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            presets: [
                                '@babel/preset-env',
                                '@babel/preset-react',
                                '@babel/preset-typescript'
                            ]
                        }
                    }
                },
                {
                    test: /\.jsx?$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader'
                    }
                },
                {
                    test: /\.(jsx?|mjs)$/,
                    include: /node_modules[\\\/](react-jsx-parser|highlight[.]js|react-markdown|remark-math|is-plain-obj|color|date-fns|@radix-ui|@floating-ui|react-window)[\\\/]/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            babelrc: false,
                            configFile: false,
                            presets: [
                                ['@babel/preset-env', {
                                    targets: {
                                        browsers: ['last 10 years and not dead']
                                    },
                                    modules: false
                                }]
                            ]
                        }
                    }
                },
                {
                    test: /\.css$/,
                    use: [
                        {
                            loader: 'style-loader',
                            options: {
                                insert: function insertAtTop(element) {
                                    var parent = document.querySelector('head');
                                    // eslint-disable-next-line no-underscore-dangle
                                    var lastInsertedElement =
                                        window._lastElementInsertedByStyleLoader;

                                    if (!lastInsertedElement) {
                                        parent.insertBefore(element, parent.firstChild);
                                    } else if (lastInsertedElement.nextSibling) {
                                        parent.insertBefore(element, lastInsertedElement.nextSibling);
                                    } else {
                                        parent.appendChild(element);
                                    }

                                    // eslint-disable-next-line no-underscore-dangle
                                    window._lastElementInsertedByStyleLoader = element;
                                }
                            }
                        },
                        {
                            loader: 'css-loader',
                        },
                    ],
                },
            ],
        },
        optimization: {
            splitChunks: {
                name: '[name].js',
                cacheGroups: {
                    async: {
                        chunks: 'async',
                        minSize: 0,
                        name(module, chunks, cacheGroupKey) {
                            return `${cacheGroupKey}-${chunks[0].name}`;
                        }
                    },
                    shared: {
                        chunks: 'all',
                        minSize: 0,
                        minChunks: 2,
                        name: 'dash_core_components-shared'
                    }
                }
            }
        },
        plugins: [
            new WebpackDashDynamicImport(),
            new webpack.SourceMapDevToolPlugin({
                filename: '[file].map',
                exclude: ['async-plotlyjs', 'async-mathjax']
            }),
            new NodePolyfillPlugin()
        ]
    }
};
