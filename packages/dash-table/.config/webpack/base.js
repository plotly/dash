const path = require('path');
const WebpackDashDynamicImport = require('@plotly/webpack-dash-dynamic-import');

const basePreprocessing = require('./base.preprocessing');
const packagejson = require('./../../package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');


module.exports = (options = {}) => {
    const babel = options.babel || undefined;
    const preprocessor = basePreprocessing(options.preprocessor);
    const mode = options.mode || 'development';
    const ts = options.ts || {};

    console.log('********** Webpack Environment Overrides **********');
    console.log('Preprocessor', JSON.stringify(preprocessor));
    console.log('mode', mode);
    console.log('babel', JSON.stringify(babel));
    console.log('ts', JSON.stringify(ts));

    return {
        entry: {
            bundle: './src/dash-table/index.ts',
            demo: ['./demo/index.html', './demo/index.js']
        },
        mode: mode,
        output: {
            path: path.resolve(__dirname, `./../../${dashLibraryName}`),
            chunkFilename: '[name].js',
            filename: '[name].js',
            library: dashLibraryName,
            libraryTarget: 'window'
        },
        devtool: 'source-map',
        externals: {
            react: 'React',
            'react-dom': 'ReactDOM',
            'plotly.js': 'Plotly'
        },
        module: {
            rules: [
                {
                    test: /demo[/\\]index.html?$/,
                    loader: 'file-loader?name=index.[ext]'
                },
                {
                    test: /\.csv$/,
                    loader: 'raw-loader'
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
                cypress: path.resolve('./tests/cypress/src'),
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
                name: true,
                cacheGroups: {
                    async: {

                    }
                }
            }
        },
        plugins: [
            new WebpackDashDynamicImport()
        ]
    };
};