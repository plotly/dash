'use strict';

var compose = require('ramda').compose;

var baseConfig = require('./webpack.config');
var babel = require('./partials/babel');
var cleanBuild = require('./partials/cleanBuild')
var defineEnv = require('./partials/defineEnv');
var entryProd = require('./partials/entryProd');
var optimizeProd = require('./partials/optimizeProd');
var outputProd = require('./partials/outputProd');

// TODO: support locally served source maps in production (#11)
module.exports = compose(
    babel,
    cleanBuild,
    defineEnv,
    entryProd,
    outputProd,
    optimizeProd
)(baseConfig);
