'use strict';

export default {
    resolve: (componentName, namespace) => {
        const ns = window[namespace]; /* global window: true */

        if (ns) {
            if (ns[componentName]) {
                return ns[componentName];
            }

            throw new Error(`Component ${componentName} not found in
                ${namespace}`);
        }

        throw new Error(`${namespace} was not found.`);
    },
};
