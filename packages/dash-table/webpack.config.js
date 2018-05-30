const path = require('path');
const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

module.exports = {
    entry: {main: './src/lib/index.js'},
    output: {
        path: path.resolve(__dirname, dashLibraryName),
        filename: 'bundle.js',
        library: dashLibraryName,
        libraryTarget: 'window',
    },
    externals: {
        react: 'React',
        'react-dom': 'ReactDOM',
        'plotly.js': 'Plotly',
    },
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
                use: [
                    {
                        loader: 'style-loader',
                    },
                    {
                        loader: 'css-loader',
                    },
                ],
            },
        ],
    },
};
