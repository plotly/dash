const path = require('path');
const webpack = require('webpack');
const WebpackDashDynamicImport = require('@plotly/webpack-dash-dynamic-import');

const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

module.exports = {
    entry: { main: './src/index.js' },
    externals: {
        react: 'React',
        'react-dom': 'ReactDOM',
        'prop-types': 'PropTypes'
    },
    output: {
        path: path.resolve(__dirname, dashLibraryName),
        chunkFilename: '[name].js',
        filename: `${dashLibraryName}.js`,
        library: {
            name: dashLibraryName,
            type: 'window',
        }
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader'
                }
            }
        ],
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
