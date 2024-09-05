export default {
    resolve: component => {
        const {type, namespace} = component;

        const ns = window[namespace];

        if (ns) {
            if (ns[type]) {
                return ns[type];
            }

            throw new Error(`Component ${type} not found in ${namespace}`);
        }

        throw new Error(`${namespace} was not found.`);
    }
};
