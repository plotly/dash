const path = require('path');
const WebpackDashDynamicImport = require('@plotly/webpack-dash-dynamic-import');

const basePreprocessing = require('./base.preprocessing');
const packagejson = require('./../../package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');


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
        devtool: 'source-map',
        externals: {
            react: 'React',
            'react-dom': 'ReactDOM',
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
                        { loader: 'babel-loader', options: babel },
                        { loader: 'ts-loader', options: ts },
                    ]
                },
                {
                    test: /\.ts(x?)$/,
                    exclude: /node_modules/,
                    use: [
                        { loader: 'babel-loader', options: babel },
                        { loader: 'ts-loader', options: ts },
                        { loader: 'webpack-preprocessor', options: JSON.stringify(preprocessor) }
                    ]
                },
                {
                    test: /\.js$/,
                    include: /node_modules[\\\/](highlight[.]js|d3-format)[\\\/]/,
                    use: [
                        { loader: 'babel-loader', options: babel }
                    ]
                },
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    use: [
                        { loader: 'babel-loader', options: babel },
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
