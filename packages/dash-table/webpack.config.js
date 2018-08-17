const path = require('path');
const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

module.exports = {
    entry: {
        bundle: './src/dash-table/index.js',
        demo: ['./demo/index.js', './demo/index.html'],
    },
    output: {
        path: path.resolve(__dirname, dashLibraryName),
        filename: '[name].js',
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
                test: /demo[/]index.html?$/,
                loader: 'file-loader?name=index.[ext]'
            },
            {
                test: /\.ts(x?)$/,
                exclude: /node_modules/,
                use: [
                    { loader: 'babel-loader' },
                    { loader: 'ts-loader' }
                ]
            },
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
                    { loader: 'style-loader' },
                    { loader: 'css-loader' }
                ],
            },
            {
                test: /\.less$/,
                use: [
                    { loader: 'style-loader' },
                    { loader: 'css-loader' },
                    { loader: 'less-loader' }
                ],
            },
        ],
    },
    resolve: {
        alias: {
            'dash-table': path.resolve('./src/dash-table'),
            'core': path.resolve('./src/core'),
            'tests': path.resolve('./tests')
        },
        extensions: ['.js', '.ts', '.tsx']
    }
};
