
import React, {PropTypes} from 'react';

const Canvas = (props) => (
    <canvas {...props}>
        {props.children}
    </canvas>
);

Canvas.propTypes = {

    /**
     * Specifies the height of elements listed here. For all other elements, use the CSS height property.        Note: In some instances, such as <div>, this is a legacy attribute, in which case the CSS heightproperty should be used instead.
     */
    'height': PropTypes.string,
        

    /**
     * For the elements listed here, this establishes the element's width.        Note: For all other instances, such as <div>, this is a legacy attribute, in which case the CSS widthproperty should be used instead.
     */
    'width': PropTypes.string
        
};

export default Canvas;
    