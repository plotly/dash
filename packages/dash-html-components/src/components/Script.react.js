
import React, {PropTypes} from 'react';

const Script = (props) => (
    <script {...props}>
        {props.children}
    </script>
);

Script.propTypes = {

    /**
     * Indicates that the script should be executed asynchronously.
     */
    'async': PropTypes.string,
        

    /**
     * Declares the character encoding of the page or script.
     */
    'charset': PropTypes.string,
        

    /**
     * Indicates that the script should be executed after the page has been parsed.
     */
    'defer': PropTypes.string,
        

    /**
     * Defines the script language used in the element.
     */
    'language': PropTypes.string,
        

    /**
     * The URL of the embeddable content.
     */
    'src': PropTypes.string,
        

    /**
     * Defines the type of the element.
     */
    'type': PropTypes.string
        
};

export default Script;
    