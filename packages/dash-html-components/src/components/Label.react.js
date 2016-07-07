
import React, {PropTypes} from 'react';

const Label = (props) => (
    <label {...props}>
        {props.children}
    </label>
);

Label.propTypes = {

    /**
     * Describes elements which belongs to this one.
     */
    'htmlFor': PropTypes.string,
        

    /**
     * Indicates the form that is the owner of the element.
     */
    'form': PropTypes.string
        
};

export default Label;
    