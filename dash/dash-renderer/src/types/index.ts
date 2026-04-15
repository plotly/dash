import {DashComponentApi} from './component';

declare global {
    interface Window {
        dash_component_api: DashComponentApi;
    }
}

export * from './component';
export * from './callbacks';
