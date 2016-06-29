
import React, {PropTypes} from 'react';

const Fieldset = (props) => (
    <fieldset {...props}>
        {props.children}
    </fieldset>
);

Fieldset.propTypes = {

    /**
     * Indicates whether the user can interact with the element.
     */
    'disabled': PropTypes.string,
        

    /**
     * Indicates the form that is the owner of the element.
     */
    'form': PropTypes.string,
        

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string
        
};

export default Fieldset;
    