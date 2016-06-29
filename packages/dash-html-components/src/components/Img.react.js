
import React, {PropTypes} from 'react';

const Img = (props) => (
    <img {...props}>
        {props.children}
    </img>
);

Img.propTypes = {

    /**
     * Specifies the horizontal alignment of the element.
     */
    'align': PropTypes.string,
        

    /**
     * Alternative text in case an image can't be displayed.
     */
    'alt': PropTypes.string,
        

    /**
     * The border width.        Note: This is a legacy attribute. Please use the CSS border property instead.
     */
    'border': PropTypes.string,
        

    /**
     * Specifies the height of elements listed here. For all other elements, use the CSS height property.        Note: In some instances, such as <div>, this is a legacy attribute, in which case the CSS heightproperty should be used instead.
     */
    'height': PropTypes.string,
        

    /**
     * Indicates that the image is part of a server-side image map.
     */
    'ismap': PropTypes.string,
        

    /**
     * 
     */
    'sizes': PropTypes.string,
        

    /**
     * The URL of the embeddable content.
     */
    'src': PropTypes.string,
        

    /**
     * 
     */
    'srcset': PropTypes.string,
        

    /**
     * 
     */
    'usemap': PropTypes.string,
        

    /**
     * For the elements listed here, this establishes the element's width.        Note: For all other instances, such as <div>, this is a legacy attribute, in which case the CSS widthproperty should be used instead.
     */
    'width': PropTypes.string
        
};

export default Img;
    