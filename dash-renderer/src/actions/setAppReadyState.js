import {path} from 'ramda';
import {createAction} from 'redux-actions';

import Registry from './../registry';
import {getAction} from './constants';
import {isReady} from '@plotly/dash-component-plugins';

const isAppReady = (layout, paths) => targets => {
    if (!layout || !paths || !Array.isArray(targets)) {
        return true;
    }

    const promises = [];
    targets.forEach(id => {
        const pathOfId = paths[id];
        if (!pathOfId) {
            return;
        }

        const target = path(pathOfId, layout);
        if (!target) {
            return;
        }

        const component = Registry.resolve(target);
        const ready = isReady(component);

        if (ready && typeof ready.then === 'function') {
            promises.push(ready);
        }
    });

    return promises.length ? Promise.all(promises) : true;
};

const setAction = createAction(getAction('SET_APP_READY'));

export default () => async (dispatch, getState) => {
    const {layout, paths} = getState();
    const ready = isAppReady(layout, paths);

    dispatch(setAction(ready));
};
