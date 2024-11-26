import React, {createRef, useEffect, useMemo} from 'react';
import PropTypes from 'prop-types';

const ResizeDetector = props => {
    const {onResize, children} = props;
    const ref = createRef();

    const observer = useMemo(
        () =>
            new ResizeObserver(() => {
                onResize();
            }),
        [onResize]
    );

    useEffect(() => {
        if (!ref.current) {
            return () => {};
        }
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
};

export default ResizeDetector;
