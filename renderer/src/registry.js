'use strict';

import {
    B,
    Div,
    H1,
    H2,
    P,
    Pre,
    Span,
    Strong
} from 'dash-html-components/lib';

export default {
    B,
    Div,
    H1,
    H2,
    P,
    Pre,
    Span,
    Strong,

    resolve: (componentName, namespace) => {
        const ns = window[namespace];

        if (ns) {
            if (ns[componentName]) {
                return ns[componentName];
            }

            throw new Error(`Component ${componentName} not found in
                ${namespace}`);
        }

        throw new Error(`${namespace} was not found, make sure to
            \`pip install ${namespace}\` and pass it as string in the
            \`component_suites\` kwarg to \`dash.run_server\`.`);
    }
};
