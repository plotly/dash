
import React, {PropTypes} from 'react';

const Form = (props) => (
    <form {...props}>
        {props.children}
    </form>
);

Form.propTypes = {

    /**
     * List of types the server accepts, typically a file type.
     */
    'accept': PropTypes.string,
        

    /**
     * List of supported charsets.
     */
    'acceptCharset': PropTypes.string,
        

    /**
     * The URI of a program that processes the information submitted via the form.
     */
    'action': PropTypes.string,
        

    /**
     * Indicates whether controls in this form can by default have their values automatically completed by the browser.
     */
    'autocomplete': PropTypes.string,
        

    /**
     * Defines the content type of the form date when the method is POST.
     */
    'enctype': PropTypes.string,
        

    /**
     * Defines which HTTP method to use when submitting the form. Can be GET (default) or POST.
     */
    'method': PropTypes.string,
        

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string,
        

    /**
     * This attribute indicates that the form shouldn't be validated when submitted.
     */
    'novalidate': PropTypes.string,
        

    /**
     * 
     */
    'target': PropTypes.string
        
};

export default Form;
    