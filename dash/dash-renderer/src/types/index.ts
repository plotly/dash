import {DashComponentApi} from './component';

export interface DashClientside {
    clean_url: (url: string, fallback?: string) => string;
}

declare global {
    interface Window {
        dash_component_api: DashComponentApi;
        dash_clientside: DashClientside;
    }
}

export * from './component';
export * from './callbacks';
