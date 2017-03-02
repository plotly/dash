import R from 'ramda';

const extend = R.reduce(R.flip(R.append))

// crawl a layout object, apply a function on every object
export const crawlLayout = (object, func, path=[]) => {
    func(object, path);

    /*
     * object may be a string, a number, or null
     * R.has will return false for both of those types
     */
    if (R.type(object) === 'Object' &&
        R.has('props', object) &&
        R.has('content', object.props)
    ) {
        const newPath = extend(path, ['props', 'content']);
        if (Array.isArray(object.props.content)) {
            object.props.content.forEach((child, i) => {
                crawlLayout(
                    child,
                    func,
                    R.append(i, newPath));
            });
        } else {
            crawlLayout(
                object.props.content,
                func,
                newPath
            );
        }

    }
}
