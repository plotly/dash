import R from 'ramda';

const extend = R.reduce(R.flip(R.append));

const hasProps = R.allPass([R.is(Object), R.has('props')]);

export const hasPropsId = R.allPass([
    hasProps,
    R.compose(
        R.has('id'),
        R.prop('props')
    ),
]);

export const hasPropsChildren = R.allPass([
    hasProps,
    R.compose(
        R.has('children'),
        R.prop('props')
    ),
]);

// crawl a layout object, apply a function on every object
export const crawlLayout = (object, func, path = []) => {
    func(object, path);

    /*
     * object may be a string, a number, or null
     * R.has will return false for both of those types
     */
    if (hasPropsChildren(object)) {
        const newPath = extend(path, ['props', 'children']);
        if (Array.isArray(object.props.children)) {
            object.props.children.forEach((child, i) => {
                crawlLayout(child, func, R.append(i, newPath));
            });
        } else {
            crawlLayout(object.props.children, func, newPath);
        }
    } else if (R.is(Array, object)) {
        /*
         * Sometimes when we're updating a sub-tree
         * (like when we're responding to a callback)
         * that returns `{children: [{...}, {...}]}`
         * then we'll need to start crawling from
         * an array instead of an object.
         */

        object.forEach((child, i) => {
            crawlLayout(child, func, R.append(i, path));
        });
    }
};

export function hasId(child) {
    return (
        R.type(child) === 'Object' &&
        R.has('props', child) &&
        R.has('id', child.props)
    );
}
