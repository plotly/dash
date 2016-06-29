
import React, {PropTypes} from 'react';

const Q = (props) => (
    <q {...props}>
        {props.children}
    </q>
);

Q.propTypes = {

    /**
     * Contains a URI which points to the source of the quote or change.
     */
    'cite': PropTypes.string
        
};

export default Q;
    