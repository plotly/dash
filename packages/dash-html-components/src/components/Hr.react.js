
import React, {PropTypes} from 'react';

const Hr = (props) => (
    <hr {...props}>
        {props.children}
    </hr>
);

Hr.propTypes = {

    /**
     * Specifies the horizontal alignment of the element.
     */
    'align': PropTypes.string,
        

    /**
     * This attribute sets the text color using either a named color or a color specified in the hexadecimal #RRGGBB format.        Note: This is a legacy attribute. Please use the CSS color property instead.
     */
    'color': PropTypes.string
        
};

export default Hr;
    