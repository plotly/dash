import React from 'react';
import PropTypes from 'prop-types';

const ArrayOfExactOrShapeWithNodePropAssignNone = (props) => {
    const { id, test_array_of_exact_prop, test_array_of_shape_prop } = props;

    return (
        <div id={id}>
            {`length of test_array_of_exact_prop: ${(test_array_of_exact_prop || []).length}, length of test_array_of_shape_prop: ${(test_array_of_shape_prop || []).length}`}
        </div>
    );
};

ArrayOfExactOrShapeWithNodePropAssignNone.propTypes = {
    id: PropTypes.string,
    test_array_of_exact_prop: PropTypes.arrayOf(
        PropTypes.exact({
            label: PropTypes.node,
            value: PropTypes.string
        })
    ),
    test_array_of_shape_prop: PropTypes.arrayOf(
        PropTypes.shape({
            label: PropTypes.node,
            value: PropTypes.string
        })
    )
};

export default ArrayOfExactOrShapeWithNodePropAssignNone;
