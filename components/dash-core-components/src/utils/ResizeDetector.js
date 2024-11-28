import React, {createRef, useEffect, useMemo} from 'react';
import PropTypes from 'prop-types';

const ResizeDetector = props => {
    const {onResize, autosize, children, targets} = props;
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
        targets.forEach(target => observer.observe(target.current));
        observer.observe(ref.current);
        const windowResizedHandled = -1;
        // if (autosize) {
        //     windowResizedHandled = window.addEventListener(
        //         'resize',
        //         onResize
        //     );
        // }
        return () => {
            observer.disconnect();
            if (autosize) {
                window.removeEventListener(windowResizedHandled);
            }
        };
    }, [ref.current]);

    return (
        <div ref={ref} style={{width: '100%'}}>
            {children}
        </div>
    );
};

ResizeDetector.propTypes = {
    autosize: PropTypes.bool,
    onResize: PropTypes.func,
    children: PropTypes.node,
    targets: PropTypes.any,
};

export default ResizeDetector;
