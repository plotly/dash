import R from 'ramda';

const pad = R.curry((array, paddingValues) => array.reduce((r, v) => {
    paddingValues.forEach(paddingValue => r.push(paddingValue));
    r.push(v);
    return r;
}, []));

// crawl a layout object, apply a function on every object
export const crawlLayout = (object, func, path=[]) => {
    func(object, path);
    if (Array.isArray(object.props.content)) {
        object.props.content.forEach((child, i) => {
            crawlLayout(child, func, R.append(i, path));
        });
    }
}

export const createTreePath = (array) => pad(array, ['props', 'content']);
