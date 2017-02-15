/* eslint-disable import/default */
/* global require:false */
import karmaRunner from 'dash-components-archetype-dev/karma-runner';

karmaRunner.setupEnvironment();

// Use webpack to infer and `require` tests automatically.
var testsReq = require.context('../src', true, /\.test.js$/);
testsReq.keys().map(testsReq);

karmaRunner.startKarma();
