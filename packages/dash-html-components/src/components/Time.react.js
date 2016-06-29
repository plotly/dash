
import React, {PropTypes} from 'react';

const Time = (props) => (
    <time {...props}>
        {props.children}
    </time>
);

Time.propTypes = {

    /**
     * Indicates the date and time associated with the element.
     */
    'datetime': PropTypes.string
        
};

export default Time;
    