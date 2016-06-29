
import React, {PropTypes} from 'react';

const Button = (props) => (
    <button {...props}>
        {props.children}
    </button>
);

Button.propTypes = {

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
     * Indicates the action of the element, overriding the action defined in the <form>.
     */
    'formaction': PropTypes.string,
        

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string,
        

    /**
     * Defines the type of the element.
     */
    'type': PropTypes.string,
        

    /**
     * Defines a default value which will be displayed in the element on page load.
     */
    'value': PropTypes.string
        
};

export default Button;
    