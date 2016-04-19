module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'main.js',
    path: './static/',
    publicPath: 'static/'
  },
  devtool: 'source-map',
  module: {
    loaders: [
      { test: /\.js$/, exclude: /node_modules/, loader: "babel-loader" },
      { test: /\.json$/, loader: 'json-loader' }
    ]
  },
  node: {
    console: 'empty',
    fs: 'empty',
    net: 'empty',
    tls: 'empty'
  }
};
