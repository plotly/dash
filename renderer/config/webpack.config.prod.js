'use strict';

var compose = require('ramda').compose;

var babel = require('../../config/partials/babel');
var cleanBuild = require('../../config/partials/cleanBuild')
var defineEnv = require('../../config/partials/defineEnv');
var entryProd = require('../../config/partials/entryProd');
var optimizeProd = require('../../config/partials/optimizeProd');
var outputProd = require('../../config/partials/outputProd');
var baseConfig = require('./webpack.config');

// TODO: support locally served source maps in production (#11)
module.exports = compose(
    babel,
    cleanBuild,
    defineEnv,
    entryProd,
    outputProd,
    optimizeProd
)(baseConfig);
