import {has, type} from 'ramda';

/*
 * requests_pathname_prefix is the new config parameter introduced in
 * dash==0.18.0. The previous versions just had url_base_pathname
 */
export function urlBase(config) {
    if (
        type(config) === 'Null' ||
        (type(config) === 'Object' &&
            !has('url_base_pathname', config) &&
            !has('requests_pathname_prefix', config))
    ) {
        throw new Error(
            `
            Trying to make an API request but "url_base_pathname" and
            "requests_pathname_prefix"
            is not in \`config\`. \`config\` is: `,
            config
        );
    } else if (
        has('url_base_pathname', config) &&
        !has('requests_pathname_prefix', config)
    ) {
        return config.url_base_pathname;
    } else if (has('requests_pathname_prefix', config)) {
        return config.requests_pathname_prefix;
    } else {
        throw new Error(
            `Unhandled case trying to get url_base_pathname or
             requests_pathname_prefix from config`,
            config
        );
    }
}

export function uid() {
    function s4() {
        const h = 0x10000;
        return Math.floor((1 + Math.random()) * h)
            .toString(16)
            .substring(1);
    }
    return (
        s4() +
        s4() +
        '-' +
        s4() +
        '-' +
        s4() +
        '-' +
        s4() +
        '-' +
        s4() +
        s4() +
        s4()
    );
}

export function isMultiOutputProp(outputIdAndProp) {
    /*
     * If this update is for multiple outputs, then it has
     * starting & trailing `..` and each propId pair is separated
     * by `...`, e.g.
     * "..output-1.value...output-2.value...output-3.value...output-4.value.."
     */

    return outputIdAndProp.startsWith('..');
}

export function parseMultipleOutputs(outputIdAndProp) {
    /*
     * If this update is for multiple outputs, then it has
     * starting & trailing `..` and each propId pair is separated
     * by `...`, e.g.
     * "..output-1.value...output-2.value...output-3.value...output-4.value.."
     */
    return outputIdAndProp
        .split('...')
        .map(o => o.replace('..', ''));
}
