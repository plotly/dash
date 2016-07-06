
import React, {PropTypes} from 'react';

const Input = (props) => (
    <input {...props}>
        {props.children}
    </input>
);

Input.propTypes = {

    /**
     * List of types the server accepts, typically a file type.
     */
    'accept': PropTypes.string,
        

    /**
     * Alternative text in case an image can't be displayed.
     */
    'alt': PropTypes.string,
        

    /**
     * Indicates whether controls in this form can by default have their values automatically completed by the browser.
     */
    'autocomplete': PropTypes.string,
        

    /**
     * The element should be automatically focused after the page loaded.
     */
    'autofocus': PropTypes.string,
        

    /**
     * Previous values should persist dropdowns of selectable values across page loads.
     */
    'autosave': PropTypes.string,
        

    /**
     * Indicates whether the element should be checked on page load.
     */
    'checked': PropTypes.string,
        

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
     * Indicates the action of the element, overriding the action defined in the <form>.
     */
    'formaction': PropTypes.string,
        

    /**
     * Specifies the height of elements listed here. For all other elements, use the CSS height property.        Note: In some instances, such as <div>, this is a legacy attribute, in which case the CSS height property should be used instead.
     */
    'height': PropTypes.string,
        

    /**
     * Identifies a list of pre-defined options to suggest to the user.
     */
    'list': PropTypes.string,
        

    /**
     * Indicates the maximum value allowed.
     */
    'max': PropTypes.string,
        

    /**
     * Defines the maximum number of characters allowed in the element.
     */
    'maxlength': PropTypes.string,
        

    /**
     * Indicates the minimum value allowed.
     */
    'min': PropTypes.string,
        

    /**
     * Indicates whether multiple values can be entered in an input of the type email or file.
     */
    'multiple': PropTypes.string,
        

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string,
        

    /**
     * Defines a regular expression which the element's value will be validated against.
     */
    'pattern': PropTypes.string,
        

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
     * Defines the width of the element (in pixels). If the element's type attribute is text or password then it's the number of characters.
     */
    'size': PropTypes.string,
        

    /**
     * The URL of the embeddable content.
     */
    'src': PropTypes.string,
        

    /**
     * 
     */
    'step': PropTypes.string,
        

    /**
     * Defines the type of the element.
     */
    'type': PropTypes.string,
        

    /**
     * 
     */
    'usemap': PropTypes.string,
        

    /**
     * Defines a default value which will be displayed in the element on page load.
     */
    'value': PropTypes.string,
        

    /**
     * For the elements listed here, this establishes the element's width.        Note: For all other instances, such as <div>, this is a legacy attribute, in which case the CSS width property should be used instead.
     */
    'width': PropTypes.string
        
};

export default Input;
    