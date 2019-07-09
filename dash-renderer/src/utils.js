import {has, type} from 'ramda';

/*
 * requests_pathname_prefix is the new config parameter introduced in
 * dash==0.18.0. The previous versions just had url_base_pathname
 */
export function urlBase(config) {
    const hasUrlBase = has('url_base_pathname', config);
    const hasReqPrefix = has('requests_pathname_prefix', config);
    if (type(config) !== 'Object' || (!hasUrlBase && !hasReqPrefix)) {
        throw new Error(
            `
            Trying to make an API request but neither
            "url_base_pathname" nor "requests_pathname_prefix"
            is in \`config\`. \`config\` is: `,
            config
        );
    }

    const base = hasReqPrefix
        ? config.requests_pathname_prefix
        : config.url_base_pathname;

    return base.charAt(base.length - 1) === '/' ? base : base + '/';
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
    return outputIdAndProp.split('...').map(o => o.replace('..', ''));
}
