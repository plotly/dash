import R from 'ramda';

const pad = R.curry((array, paddingValue) => array.reduce((r, v) => {
    r.push(paddingValue);
    r.push(v);
    return r;
}, []));

// crawl a layout object, apply a function on every object
function crawlLayout(object, func, path=[]) {
    func(object, path);
    if (Array.isArray(object.children)) {
        object.children.forEach((child, i) => {
            crawlLayout(child, func, R.append(i, path));
        });
    }
}

export default {
    createTreePath: (array) => pad(array, 'children'),
    crawlLayout
};
