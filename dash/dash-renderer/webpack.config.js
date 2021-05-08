const config = require('./webpack.base.config');

module.exports = config({
    target: ['web', 'es5']
});
