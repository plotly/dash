/**
 * Dash stream worker: a SharedWorker hosting the browser's single streaming
 * downlink, shared by every tab (see utils/streamClient and
 * utils/streamWorkerHost). Built to build/dash-stream-worker.js and served
 * through the component suites like the WebSocket worker.
 */

import {StreamClient} from '../utils/streamClient';
import {attachStreamWorkerHost} from '../utils/streamWorkerHost';

attachStreamWorkerHost(self as any, new StreamClient());
