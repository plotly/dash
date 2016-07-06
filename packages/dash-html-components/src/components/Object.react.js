
import React, {PropTypes} from 'react';

const Object = (props) => (
    <object {...props}>
        {props.children}
    </object>
);

Object.propTypes = {

    /**
     * The border width.        Note: This is a legacy attribute. Please use the CSS border property instead.
     */
    'border': PropTypes.string,
        

    /**
     * Indicates the form that is the owner of the element.
     */
    'form': PropTypes.string,
        

    /**
     * Specifies the height of elements listed here. For all other elements, use the CSS height property.        Note: In some instances, such as <div>, this is a legacy attribute, in which case the CSS height property should be used instead.
     */
    'height': PropTypes.string,
        

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string,
        

    /**
     * Defines the type of the element.
     */
    'type': PropTypes.string,
        

    /**
     * 
     */
    'usemap': PropTypes.string,
        

    /**
     * For the elements listed here, this establishes the element's width.        Note: For all other instances, such as <div>, this is a legacy attribute, in which case the CSS width property should be used instead.
     */
    'width': PropTypes.string
        
};

export default Object;
    