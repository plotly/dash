
import React, {PropTypes} from 'react';

const Select = (props) => (
    <select {...props}>
        {props.children}
    </select>
);

Select.propTypes = {

    /**
     * The element should be automatically focused after the page loaded.
     */
    'autofocus': PropTypes.string,
        

    /**
     * Indicates whether the user can interact with the element.
     */
    'disabled': PropTypes.string,
        

    /**
     * Indicates the form that is the owner of the element.
     */
    'form': PropTypes.string,
        

    /**
     * Indicates whether multiple values can be entered in an input of the type email or file.
     */
    'multiple': PropTypes.string,
        

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string,
        

    /**
     * Indicates whether this element is required to fill out or not.
     */
    'required': PropTypes.string,
        

    /**
     * Defines the width of the element (in pixels). If the element's type attribute is text or password then it's the number of characters.
     */
    'size': PropTypes.string
        
};

export default Select;
    