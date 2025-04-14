import React, {createRef, useEffect, useCallback, useMemo} from 'react';
import PropTypes from 'prop-types';

// Debounce 50 ms
const DELAY = 50;

const ResizeDetector = props => {
    const {onResize, children, targets} = props;
    const ref = createRef();
    let resizeTimeout;

    const debouncedResizeHandler = useCallback(() => {
        if (resizeTimeout) {
            clearTimeout(resizeTimeout);
        }
        resizeTimeout = setTimeout(() => {
            onResize(true); // Force on resize.
        }, DELAY);
    }, [onResize]);

    const observer = useMemo(
        () => new ResizeObserver(debouncedResizeHandler),
        [onResize]
    );

    useEffect(() => {
        if (!ref.current) {
            return () => {};
        }
        targets.forEach(target => observer.observe(target.current));
        observer.observe(ref.current);
        return () => {
            observer.disconnect();
        };
    }, [ref.current]);

    return <div ref={ref}>{children}</div>;
};

ResizeDetector.propTypes = {
    onResize: PropTypes.func,
    children: PropTypes.node,
    targets: PropTypes.any,
};

export default ResizeDetector;
