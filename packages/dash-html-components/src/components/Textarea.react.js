
import React, {PropTypes} from 'react';

const Textarea = (props) => (
    <textarea {...props}>
        {props.children}
    </textarea>
);

Textarea.propTypes = {

    /**
     * The element should be automatically focused after the page loaded.
     */
    'autofocus': PropTypes.string,
        

    /**
     * Defines the number of columns in a textarea.
     */
    'cols': PropTypes.string,
        

    /**
     * 
     */
    'dirname': PropTypes.string,
        

    /**
     * Indicates whether the user can interact with the element.
     */
    'disabled': PropTypes.string,
        

    /**
     * Indicates the form that is the owner of the element.
     */
    'form': PropTypes.string,
        

    /**
     * Defines the maximum number of characters allowed in the element.
     */
    'maxlength': PropTypes.string,
        

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string,
        

    /**
     * Provides a hint to the user of what can be entered in the field.
     */
    'placeholder': PropTypes.string,
        

    /**
     * Indicates whether the element can be edited.
     */
    'readonly': PropTypes.string,
        

    /**
     * Indicates whether this element is required to fill out or not.
     */
    'required': PropTypes.string,
        

    /**
     * Defines the number of rows in a text area.
     */
    'rows': PropTypes.string,
        

    /**
     * Indicates whether the text should be wrapped.
     */
    'wrap': PropTypes.string
        
};

export default Textarea;
    