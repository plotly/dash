const path = require('path');
const webpack = require('webpack');
const NodePolyfillPlugin = require("node-polyfill-webpack-plugin");
const WebpackDashDynamicImport = require('@plotly/webpack-dash-dynamic-import');

const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

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
            extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
            alias: {
                'react/jsx-runtime': require.resolve('react/jsx-runtime'),
                'react/jsx-dev-runtime': require.resolve('react/jsx-dev-runtime'),
            }
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
                    include: /node_modules[\\\/](react-jsx-parser|highlight[.]js|react-markdown|remark-math|is-plain-obj|color|date-fns|@radix-ui|@floating-ui)[\\\/]/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            babelrc: false,
                            configFile: false,
                            presets: [
                                ['@babel/preset-env', {
                                    targets: {
                                        browsers: ['last 9 years and not dead']
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
