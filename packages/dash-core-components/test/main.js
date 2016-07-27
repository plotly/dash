/* eslint-disable import/default */
/* global require:false */
import karmaRunner from 'dash-components-archetype-dev/karma-runner';

karmaRunner.setupEnvironment();

// --------------------------------------------------------------------------
// Bootstrap
// --------------------------------------------------------------------------
// Use webpack to include all app code _except_ the entry point so we can get
// code coverage in the bundle, whether tested or not.
// TODO: This doesn't seem to work.
var srcReq = require.context('../src', true, /\.js$/);
srcReq.keys().map(srcReq);

// Use webpack to infer and `require` tests automatically.
var testsReq = require.context('../src', true, /\.test.js$/);
testsReq.keys().map(testsReq);

karmaRunner.startKarma();
