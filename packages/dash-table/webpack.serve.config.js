const config = require('./webpack.config');

config.entry = {main: './demo/index.js'};
config.output = {filename: 'output.js'};
config.mode = 'development';
config.externals = undefined; // eslint-disable-line
config.devtool = 'inline-source-map';
module.exports = config;
