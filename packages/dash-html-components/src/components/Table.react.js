
import React, {PropTypes} from 'react';

const Table = (props) => (
    <table {...props}>
        {props.children}
    </table>
);

Table.propTypes = {

    /**
     * Specifies the horizontal alignment of the element.
     */
    'align': PropTypes.string,
        

    /**
     * Background color of the element.        Note: This is a legacy attribute. Please use the CSS background-color property instead.
     */
    'bgcolor': PropTypes.string,
        

    /**
     * The border width.        Note: This is a legacy attribute. Please use the CSS border property instead.
     */
    'border': PropTypes.string,
        

    /**
     * 
     */
    'summary': PropTypes.string
        
};

export default Table;
    