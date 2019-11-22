import {filter} from 'ramda';
import {createAction} from 'redux-actions';

import isSimpleComponent from '../isSimpleComponent';
import Registry from './../registry';
import {getAction} from './constants';
import {isReady} from '@plotly/dash-component-plugins';

const isAppReady = layout => {
    const queue = [layout];

    const components = {};
    const ids = {};

    /* Would be much simpler if the Registry was aware of what it contained... */
    while (queue.length) {
        const elementLayout = queue.shift();
        if (!elementLayout) {
            continue;
        }

        const id = elementLayout.props && elementLayout.props.id;
        const children = elementLayout.props && elementLayout.props.children;
        const namespace = elementLayout.namespace;
        const type = elementLayout.type;

        components[namespace] = components[namespace] || {};
        components[namespace][type] = type;

        if (id) {
            ids[id] = {namespace, type};
        }

        if (children) {
            const filteredChildren = filter(
                child => !isSimpleComponent(child),
                Array.isArray(children) ? children : [children]
            );

            queue.push(...filteredChildren);
        }
    }

    return targets => {
        const promises = [];

        if (Array.isArray(targets)) {
            targets.forEach(id => {
                const target = ids[id];
                if (target) {
                    const component = Registry.resolve(target);

                    const ready = isReady(component);

                    if (ready && typeof ready.then === 'function') {
                        promises.push(ready);
                    }
                }
            });
        } else {
            Object.entries(components).forEach(([namespace, item]) => {
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
        }

        return promises.length ? Promise.all(promises) : true;
    };
};

const setAction = createAction(getAction('SET_APP_READY'));

export default () => async (dispatch, getState) => {
    const ready = isAppReady(getState().layout);

    dispatch(setAction(ready));
};
