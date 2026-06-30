const config = require('./webpack.config.js');
const path = require('path');

config.entry = { main: './src/demo/index.js' };
config.output = {
    filename: 'output.js',
    path: path.resolve(__dirname, 'inst', 'deps'),
};
config.mode = 'development';
config.externals = undefined; // eslint-disable-line
config.devtool = 'inline-source-map';
module.exports = config;
