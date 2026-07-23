import './react-shim'; // Fallback; normally loaded standalone right after React
import {DashRenderer} from './DashRenderer';
import './utils/clientsideFunctions';

// make DashRenderer globally available
window.DashRenderer = DashRenderer;
