
import React, {PropTypes} from 'react';

const Li = (props) => (
    <li {...props}>
        {props.children}
    </li>
);

Li.propTypes = {

    /**
     * Defines a default value which will be displayed in the element on page load.
     */
    'value': PropTypes.string
        
};

export default Li;
    