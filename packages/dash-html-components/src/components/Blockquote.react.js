
import React, {PropTypes} from 'react';

const Blockquote = (props) => (
    <blockquote {...props}>
        {props.children}
    </blockquote>
);

Blockquote.propTypes = {

    /**
     * Contains a URI which points to the source of the quote or change.
     */
    'cite': PropTypes.string
        
};

export default Blockquote;
    