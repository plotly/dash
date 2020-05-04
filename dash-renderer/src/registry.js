import { path } from 'ramda';

export default {
    resolve: component => {
        const {type, namespace} = component;

        const ns = window[namespace];

        if (ns) {
            const c = path(type.split('.'), ns);
            if (c) {
                return c;
            }

            throw new Error(`Component ${type} not found in ${namespace}`);
        }

        throw new Error(`${namespace} was not found.`);
    },
};
