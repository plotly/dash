'use strict';

var compose = require('ramda').compose;

var babel = require('../../config/partials/babel');
var defineEnv = require('../../config/partials/defineEnv');
var entryDev = require('../../config/partials/entryDev')
var outputDev = require('../../config/partials/outputDev');
var sourceMapDev = require('../../config/partials/sourceMapDev');
var baseConfig = require('./webpack.config');

module.exports = compose(
    babel,
    defineEnv,
    entryDev,
    outputDev,
    sourceMapDev
)(baseConfig);
