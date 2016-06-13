'use strict';

var compose = require('ramda').compose;

var babelHot = require('../../config/partials/babelHot');
var defineEnv = require('../../config/partials/defineEnv');
var entryHot = require('../../config/partials/entryHot');
var outputDev = require('../../config/partials/outputDev');
var sourceMapDev = require('../../config/partials/sourceMapDev');
var baseConfig = require('./webpack.config');

module.exports = compose(
    babelHot,
    defineEnv,
    entryHot,
    outputDev,
    sourceMapDev
)(baseConfig);
