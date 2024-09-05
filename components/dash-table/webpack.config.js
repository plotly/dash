let config = require('./.config/webpack/base.js')();
config.externals['prop-types'] = 'PropTypes';

module.exports = config;
