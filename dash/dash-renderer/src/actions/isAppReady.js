import {path} from 'ramda';
import {isReady} from '@plotly/dash-component-plugins';

import Registry from '../registry';
import {getPath} from './paths';
import {stringifyId} from './dependencies';

export default (layout, paths, targets) => {
    if (!targets.length) {
        return true;
    }
    const promises = [];

    const {events} = paths;
    const rendered = new Promise(resolveRendered => {
        events.once('rendered', resolveRendered);
    });

    targets.forEach(id => {
        const pathOfId = getPath(paths, id);
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
            promises.push(
                Promise.race([
                    ready,
                    rendered.then(
                        () => document.getElementById(stringifyId(id)) && ready
                    )
                ])
            );
        }
    });

    return promises.length ? Promise.all(promises) : true;
};
