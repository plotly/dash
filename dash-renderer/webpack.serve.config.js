const config = require('./webpack.config.js');

config.entry = {main: './src/demo/index.js'};
config.output = {filename: 'output.js'};
config.mode = 'development';
config.externals = undefined; // eslint-disable-line
config.devtool = 'inline-source-map';
module.exports = config;
