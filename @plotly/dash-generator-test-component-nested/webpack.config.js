const path = require('path');
const webpack = require('webpack');

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
        path: path.resolve(__dirname, dashLibraryName, 'nested'),
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
    }
};
