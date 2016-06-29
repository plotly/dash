
import React, {PropTypes} from 'react';

const A = (props) => (
    <a {...props}>
        {props.children}
    </a>
);

A.propTypes = {

    /**
     * Indicates that the hyperlink is to be used for downloading a resource.
     */
    'download': PropTypes.string,
        

    /**
     * The URL of a linked resource.
     */
    'href': PropTypes.string,
        

    /**
     * Specifies the language of the linked resource.
     */
    'hreflang': PropTypes.string,
        

    /**
     * Specifies a hint of the media for which the linked resource was designed.
     */
    'media': PropTypes.string,
        

    /**
     * 
     */
    'ping': PropTypes.string,
        

    /**
     * Specifies the relationship of the target object to the link object.
     */
    'rel': PropTypes.string,
        

    /**
     * 
     */
    'shape': PropTypes.string,
        

    /**
     * 
     */
    'target': PropTypes.string
        
};

export default A;
    