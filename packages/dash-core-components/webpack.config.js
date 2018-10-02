const path = require('path');
const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

module.exports = (env, argv) => {
    let mode;

    // if user specified mode flag take that value
    if (argv && argv.mode) {
        mode = argv.mode;
    }

    // else if configuration object is already set (module.exports) use that value
    else if (module.exports && module.exports.mode) {
        mode = module.exports = mode;
    }

    // else take webpack default
    else {
        mode = 'production';
    }
    return {
        entry: {main: './src/index.js'},
        output: {
            path: path.resolve(__dirname, dashLibraryName),
            filename:
                mode === 'development'
                    ? `${dashLibraryName}.dev.js`
                    : `${dashLibraryName}.min.js`,
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
        devtool: mode === 'development' ? 'eval-source-map' : 'none',
    };
};
