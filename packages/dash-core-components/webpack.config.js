const path = require('path');
const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

module.exports = (env, argv) => ({
    entry: {main: './src/index.js'},
    output: {
        path: path.resolve(__dirname, dashLibraryName),
        filename: argv.mode === 'development' ? `${dashLibraryName}.dev.js` : `${dashLibraryName}.min.js`,
        library: dashLibraryName,
        libraryTarget: 'window'
    },
    externals: {
        react: 'React',
        'react-dom': 'ReactDOM',
        'plotly.js': 'Plotly'
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader'
                }
            },
            {
                test: /\.css$/,
                use: [
                    {
                        loader: 'style-loader'
                    },
                    {
                        loader: 'css-loader'
                    }
                ]
            }
        ]
    },
    devtool: argv.mode === 'development' ? 'eval-source-map' : 'none'
});
