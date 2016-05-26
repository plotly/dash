'use strict';

var compose = require('ramda').compose;

var baseConfig = require('./webpack.config');
var babel = require('./partials/babel');
var entryDev = require('./partials/entryDev')
var outputDev = require('./partials/outputDev');
var sourceMapDev = require('./partials/sourceMapDev');

module.exports = compose(
    babel,
    entryDev,
    outputDev,
    sourceMapDev
)(baseConfig);
