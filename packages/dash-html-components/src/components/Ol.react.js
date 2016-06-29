
import React, {PropTypes} from 'react';

const Ol = (props) => (
    <ol {...props}>
        {props.children}
    </ol>
);

Ol.propTypes = {

    /**
     * Indicates whether the list should be displayed in a descending order instead of a ascending.
     */
    'reversed': PropTypes.string,
        

    /**
     * Defines the first number if other than 1.
     */
    'start': PropTypes.string
        
};

export default Ol;
    