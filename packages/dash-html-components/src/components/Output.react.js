
import React, {PropTypes} from 'react';

const Output = (props) => (
    <output {...props}>
        {props.children}
    </output>
);

Output.propTypes = {

    /**
     * Describes elements which belongs to this one.
     */
    'for': PropTypes.string,
        

    /**
     * Indicates the form that is the owner of the element.
     */
    'form': PropTypes.string,
        

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string
        
};

export default Output;
    