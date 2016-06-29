
import React, {PropTypes} from 'react';

const Tfoot = (props) => (
    <tfoot {...props}>
        {props.children}
    </tfoot>
);

Tfoot.propTypes = {

    /**
     * Specifies the horizontal alignment of the element.
     */
    'align': PropTypes.string,
        

    /**
     * Background color of the element.        Note: This is a legacy attribute. Please use the CSS background-color property instead.
     */
    'bgcolor': PropTypes.string
        
};

export default Tfoot;
    