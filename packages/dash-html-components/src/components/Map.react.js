
import React, {PropTypes} from 'react';

const Map = (props) => (
    <map {...props}>
        {props.children}
    </map>
);

Map.propTypes = {

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string
        
};

export default Map;
    