import {
    allPass,
    append,
    compose,
    flip,
    has,
    is,
    prop,
    reduce,
    type,
} from 'ramda';

const extend = reduce(flip(append));

const hasProps = allPass([is(Object), has('props')]);

export const hasPropsId = allPass([
    hasProps,
    compose(has('id'), prop('props')),
]);

export const hasPropsChildren = allPass([
    hasProps,
    compose(has('children'), prop('props')),
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
                crawlLayout(child, func, append(i, newPath));
            });
        } else {
            crawlLayout(object.props.children, func, newPath);
        }
    } else if (is(Array, object)) {
        /*
         * Sometimes when we're updating a sub-tree
         * (like when we're responding to a callback)
         * that returns `{children: [{...}, {...}]}`
         * then we'll need to start crawling from
         * an array instead of an object.
         */

        object.forEach((child, i) => {
            crawlLayout(child, func, append(i, path));
        });
    }
};

export function hasId(child) {
    return (
        type(child) === 'Object' &&
        has('props', child) &&
        has('id', child.props)
    );
}
