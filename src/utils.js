import {has, type} from 'ramda';

export function urlBase(config) {
    if (type(config) === "Null" ||
        (type(config) === "Object") &&
        !has('url_base_pathname', config) &&
        !has('requests_pathname_prefix', config)) {
        throw new Error(`
            Trying to make an API request but "url_base_pathname" and
            "requests_pathname_prefix"
            is not in \`config\`. \`config\` is: `, config);
    } else if (has('url_base_pathname', config) &&
        !has('requests_pathname_prefix', config)) {
        return config.url_base_pathname;
    } else if (has('requests_pathname_prefix', config)) {
        return config.requests_pathname_prefix;
    } else {
        throw new Error(
            `Unhandled case trying to get url_base_pathname or
             requests_pathname_prefix from config`, config);
    }
}
