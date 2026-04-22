import './react19-shim'; // Must be first - React 19 compatibility
import {DashRenderer} from './DashRenderer';
import './utils/clientsideFunctions';

// make DashRenderer globally available
window.DashRenderer = DashRenderer;
