import React from 'react';

/*
 * Example of a control that handles the notifyObservers prop
 */

export default props => (
    <input
        onChange={e => props.notifyObservers({value: e.target.value})}
        {...props}
    />
);
