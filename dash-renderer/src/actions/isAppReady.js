import { path } from 'ramda';
import { isReady } from '@plotly/dash-component-plugins';

import Registry from '../registry';

export default (layout, paths, targets) => {
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
