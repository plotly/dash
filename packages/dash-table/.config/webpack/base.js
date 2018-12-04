
const path = require('path');
const packagejson = require('./../../package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

module.exports = (preprocessor = {}, mode = 'development') => {
    console.log('********** Webpack Environment Overrides **********');
    console.log('Preprocessor', JSON.stringify(preprocessor));
    console.log('mode', mode);

    return {
        entry: {
            bundle: './src/dash-table/index.ts',
            demo: ['./demo/index.js', './demo/index.html'],
        },
        mode: mode,
        output: {
            path: path.resolve(__dirname, `./../../${dashLibraryName}`),
            filename: '[name].js',
            library: dashLibraryName,
            libraryTarget: 'umd'
        },
        externals: {
            react: {
                commonjs: "react",
                commonjs2: "react",
                amd: "React",
                root: "React"
            },
            "react-dom": {
                commonjs: "react-dom",
                commonjs2: "react-dom",
                amd: "ReactDOM",
                root: "ReactDOM"
            },
            'plotly.js': 'Plotly'
        },
        module: {
            rules: [
                {
                    test: /demo[/\\]index.html?$/,
                    loader: 'file-loader?name=index.[ext]'
                },
                {
                    test: /\.ts(x?)$/,
                    exclude: /node_modules/,
                    loader: `babel-loader!ts-loader!webpack-preprocessor?${JSON.stringify(preprocessor)}`
                },
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    loader: `babel-loader!webpack-preprocessor?${JSON.stringify(preprocessor)}`

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
                'cypress': path.resolve('./tests/cypress/src'),
                'dash-table': path.resolve('./src/dash-table'),
                'demo': path.resolve('./demo'),
                'core': path.resolve('./src/core'),
                'tests': path.resolve('./tests')
            },
            extensions: ['.js', '.ts', '.tsx']
        }
    };
};