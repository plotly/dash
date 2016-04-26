import React from 'react';

/*
 * Example of a control that handles the updateDependants prop
 */

export default props => (
    <input
        onChange={e => props.updateDependants({value: e.target.value})}
        {...props}
    />
);
