const path = require('path');
const WebpackDashDynamicImport = require('@plotly/webpack-dash-dynamic-import');

const basePreprocessing = require('./base.preprocessing');
const packagejson = require('./../../package.json');

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


module.exports = (options = {}) => {
    const babel = options.babel || undefined;
    const entry = options.entry || [];
    const preprocessor = basePreprocessing(options.preprocessor);
    const mode = options.mode || 'development';
    const ts = options.ts || {};

    console.log('********** Webpack Environment Overrides **********');
    console.log('options', JSON.stringify(options));

    return {
        entry: {
            bundle: entry.concat(['./src/dash-table/index.ts']),
            demo: entry.concat(['./demo/index.html', './demo/index.js'])
        },
        mode: mode,
        output: {
            path: path.resolve(__dirname, `./../../${dashLibraryName}`),
            filename: '[name].js',
            library: {
                name: dashLibraryName,
                type: 'window',
            }
        },
        devtool: mode === 'development' ? 'source-map' : false,
        externals: {
            react: 'React',
            'react-dom': 'ReactDOM',
            'react/jsx-runtime': jsxRuntimeExternal,
            'react/jsx-dev-runtime': jsxRuntimeExternal,
        },
        module: {
            rules: [
                {
                    test: /demo[\\\/]index.html?$/,
                    loader: 'file-loader',
                    options: {
                        name: 'index.[ext]'
                    }
                },
                {
                    test: /\.csv$/,
                    loader: 'raw-loader'
                },
                {
                    test: /\.ts(x?)$/,
                    include: /node_modules[\\\/](highlight[.]js|d3-format)[\\\/]/,
                    use: [
                        { loader: 'babel-loader', options: { ...babel, cacheDirectory: true } },
                        { loader: 'ts-loader', options: { ...ts, transpileOnly: true } },
                    ]
                },
                {
                    test: /\.ts(x?)$/,
                    exclude: /node_modules/,
                    use: [
                        { loader: 'babel-loader', options: { ...babel, cacheDirectory: true } },
                        { loader: 'ts-loader', options: { ...ts, transpileOnly: true } },
                        { loader: 'webpack-preprocessor', options: JSON.stringify(preprocessor) }
                    ]
                },
                {
                    test: /\.js$/,
                    include: /node_modules[\\\/](highlight[.]js|d3-format)[\\\/]/,
                    use: [
                        { loader: 'babel-loader', options: { ...babel, cacheDirectory: true } }
                    ]
                },
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    use: [
                        { loader: 'babel-loader', options: { ...babel, cacheDirectory: true } },
                        { loader: 'webpack-preprocessor', options: JSON.stringify(preprocessor) }
                    ]
                },
                {
                    test: /\.css$/,
                    use: [
                        { loader: 'style-loader' },
                        { loader: 'css-loader' }
                    ]
                },
                {
                    test: /\.less$/,
                    use: [
                        { loader: 'style-loader' },
                        { loader: 'css-loader' },
                        { loader: 'less-loader' }
                    ]
                }
            ]
        },
        cache: {
            type: 'filesystem',
            buildDependencies: {
                config: [__filename]
            }
        },
        resolve: {
            alias: {
                'dash-table': path.resolve('./src/dash-table'),
                demo: path.resolve('./demo'),
                core: path.resolve('./src/core'),
                tests: path.resolve('./tests')
            },
            extensions: ['.js', '.ts', '.tsx']
        },
        optimization: {
            splitChunks: {
                chunks: 'async',
                name: '[name].js',
                cacheGroups: {
                    async: {
                        chunks: 'async',
                        minSize: 0,
                        name(module, chunks, cacheGroupKey) {
                            return `${cacheGroupKey}-${chunks[0].name}`;
                        }
                    }
                }
            }
        },
        plugins: [
            new WebpackDashDynamicImport()
        ]
    };
};
