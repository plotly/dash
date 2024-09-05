import {
    append,
    concat,
    has,
    path,
    pathOr,
    type,
    findIndex,
    includes,
    slice
} from 'ramda';

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
                const objOf = findIndex(p => includes('{}', p), extraPath);
                if (objOf !== -1) {
                    const front = slice(0, objOf, extraPath);
                    const back = slice(objOf, extraPath.length, extraPath);
                    if (front.length) {
                        crawlLayout(
                            path(front, child),
                            func,
                            concat(currentPath, concat([i], front)),
                            back
                        );
                    } else {
                        const backPath = back
                            .map(p => p.replace('{}', ''))
                            .filter(e => e);
                        let childObj,
                            childPath = concat([i], backPath);
                        if (backPath.length) {
                            childObj = path(backPath, child);
                        } else {
                            childObj = child;
                        }
                        for (const key in childObj) {
                            const value = childObj[key];
                            crawlLayout(
                                value,
                                func,
                                concat(currentPath, childPath.concat([key]))
                            );
                        }
                    }
                } else {
                    crawlLayout(
                        path(extraPath, child),
                        func,
                        concat(currentPath, concat([i], extraPath))
                    );
                }
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
                if (childrenProp.includes('{}')) {
                    const opath = childrenProp.split('.');
                    const frontPath = [];
                    const backPath = [];
                    let found = false;

                    for (let i = 0; i < opath.length; i++) {
                        const curPath = opath[i];
                        if (!found && curPath.includes('{}')) {
                            found = true;
                            frontPath.push(curPath.replace('{}', ''));
                        } else {
                            if (found) {
                                backPath.push(curPath);
                            } else {
                                frontPath.push(curPath);
                            }
                        }
                    }
                    const newPath = concat(currentPath, [
                        'props',
                        ...frontPath
                    ]);

                    const oValue = path(['props', ...frontPath], object);
                    if (oValue !== undefined) {
                        for (const key in oValue) {
                            const value = oValue[key];
                            if (backPath.length) {
                                crawlLayout(
                                    path(backPath, value),
                                    func,
                                    concat(newPath, [key, ...backPath])
                                );
                            } else {
                                crawlLayout(value, func, [...newPath, key]);
                            }
                        }
                    }
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
