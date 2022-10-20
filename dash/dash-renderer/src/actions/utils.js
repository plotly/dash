import {append, concat, has, path, pathOr, type, path as rpath} from 'ramda';

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

const propsChildren = ['props', 'children'];

// crawl a layout object or children array, apply a function on every object
export const crawlLayout = (
    object,
    func,
    currentPath = [],
    extraPath = undefined
) => {
    if (Array.isArray(object)) {
        // children array
        object.forEach((child, i) => {
            if (extraPath) {
                crawlLayout(
                    rpath(extraPath, child),
                    func,
                    concat(currentPath, concat([i], extraPath))
                );
            } else {
                crawlLayout(child, func, append(i, currentPath));
            }
        });
    } else if (type(object) === 'Object') {
        func(object, currentPath);

        const children = path(propsChildren, object);
        if (children) {
            const newPath = concat(currentPath, propsChildren);
            crawlLayout(children, func, newPath);
        }

        const childrenProps = pathOr(
            [],
            [object.namespace, object.type],
            window.__dashprivate_childrenProps
        );
        childrenProps.forEach(childrenProp => {
            if (childrenProp.includes('[]')) {
                let [frontPath, backPath] = childrenProp
                    .split('[]')
                    .map(p => p.split('.').filter(e => e));
                const front = concat(['props'], frontPath);
                const basePath = concat(currentPath, front);
                crawlLayout(path(front, object), func, basePath, backPath);
            } else {
                const newPath = concat(currentPath, [
                    'props',
                    ...childrenProp.split('.')
                ]);
                crawlLayout(
                    path(['props', ...childrenProp.split('.')], object),
                    func,
                    newPath
                );
            }
        });
    }
};

// There are packages for this but it's simple enough, I just
// adapted it from https://gist.github.com/mudge/5830382
export class EventEmitter {
    constructor() {
        this._ev = {};
    }
    on(event, listener) {
        const events = (this._ev[event] = this._ev[event] || []);
        events.push(listener);
        return () => this.removeListener(event, listener);
    }
    removeListener(event, listener) {
        const events = this._ev[event];
        if (events) {
            const idx = events.indexOf(listener);
            if (idx > -1) {
                events.splice(idx, 1);
            }
        }
    }
    emit(event, ...args) {
        const events = this._ev[event];
        if (events) {
            events.forEach(listener => listener.apply(this, args));
        }
    }
    once(event, listener) {
        const remove = this.on(event, (...args) => {
            remove();
            listener.apply(this, args);
        });
    }
}
