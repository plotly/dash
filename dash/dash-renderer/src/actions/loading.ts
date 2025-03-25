import {createAction} from 'redux-actions';
import {DashLayoutPath} from '../types/component';

export type LoadingPayload = {
    path: DashLayoutPath;
    property: string;
    id: any;
}[];

export const loading = createAction<LoadingPayload>('LOADING');
export const loaded = createAction<LoadingPayload>('LOADED');
