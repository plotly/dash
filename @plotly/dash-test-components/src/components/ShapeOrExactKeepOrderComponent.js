import React from 'react';
import PropTypes from 'prop-types';

const ShapeOrExactKeepOrderComponent = (props) => {
    const { id } = props;

    return (
        <div id={id} />
    );
};

ShapeOrExactKeepOrderComponent.propTypes = {
    id: PropTypes.string,
    /**
     * test prop for shape
     */
    shape_test_prop: PropTypes.shape({
        /**
         * z
         */
        z: PropTypes.string,
        /**
         * a
         */
        a: PropTypes.string,
        /**
         * y
         */
        y: PropTypes.string
    }),
    /**
     * test prop for exact
     */
    exact_test_prop: PropTypes.exact({
        /**
         * z
         */
        z: PropTypes.string,
        /**
         * a
         */
        a: PropTypes.string,
        /**
         * y
         */
        y: PropTypes.string
    }),
};

export default ShapeOrExactKeepOrderComponent;
