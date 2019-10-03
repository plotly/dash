import {filter} from 'ramda';
import {createAction} from 'redux-actions';

import isSimpleComponent from '../isSimpleComponent';
import Registry from './../registry';
import {getAction} from './constants';
import {isReady} from '@plotly/dash-component-plugins';

const isAppReady = layout => {
    const queue = [layout];

    const res = {};

    /* Would be much simpler if the Registry was aware of what it contained... */
    while (queue.length) {
        const elementLayout = queue.shift();
        if (!elementLayout) {
            continue;
        }

        const children = elementLayout.props && elementLayout.props.children;
        const namespace = elementLayout.namespace;
        const type = elementLayout.type;

        res[namespace] = res[namespace] || {};
        res[namespace][type] = type;

        if (children) {
            const filteredChildren = filter(
                child => !isSimpleComponent(child),
                Array.isArray(children) ? children : [children]
            );

            queue.push(...filteredChildren);
        }
    }

    const promises = [];
    Object.entries(res).forEach(([namespace, item]) => {
        Object.entries(item).forEach(([type]) => {
            const component = Registry.resolve({
                namespace,
                type,
            });

            const ready = isReady(component);

            if (ready && typeof ready.then === 'function') {
                promises.push(ready);
            }
        });
    });

    return promises.length ? Promise.all(promises) : true;
};

const setAction = createAction(getAction('SET_APP_READY'));

export default () => async (dispatch, getState) => {
    const ready = isAppReady(getState().layout);

    if (ready === true) {
        /* All async is ready */
        dispatch(setAction(true));
    } else {
        /* Waiting on async */
        dispatch(setAction(ready));
        await ready;
        /**
         * All known async is ready.
         *
         * Callbacks were blocked while waiting, we can safely
         * assume that no update to layout happened to invalidate.
         */
        dispatch(setAction(true));
    }
};
