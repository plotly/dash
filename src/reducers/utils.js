import R from 'ramda';

const pad = R.curry((array, paddingValue) => array.reduce((r, v) => {
    r.push(paddingValue);
    r.push(v);
    return r;
}, []));

// crawl a layout object, apply a function on every object
export const crawlLayout = (object, func, path=[]) => {
    func(object, path);
    if (Array.isArray(object.children)) {
        object.children.forEach((child, i) => {
            crawlLayout(child, func, R.append(i, path));
        });
    }
}

export const createTreePath = (array) => pad(array, 'children');
